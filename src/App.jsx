import { useState } from "react"
import { v4 as uuidv4 } from 'uuid';
import './App.css'

const apiGateway = import.meta.env.VITE_APIGATEWAY;
const s3BucketName = import.meta.env.VITE_S3BUCKETNAME;
function App() {

  const [image, setImage] = useState('');
  const [uploadResultMessage, setUploadResultMessage] = useState('Please upload an image to authenticate.');
  const [visitorName, setVisitorName] = useState('placeholder.jpeg')
  const [isAuth, setAuth] = useState(false);

  function sendImage(e) {
    e.preventDefault();
    setVisitorName(image.name);
    const visitorImageName = uuidv4();
    fetch(`${apiGateway}/${s3BucketName}/${visitorImageName}.jpeg`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'image/jpeg'
      },
      body: image
    }).then(async () => {
      const response = await authenticate(visitorImageName);
      if (response.Message === 'Success') {
        setAuth(true);
        setUploadResultMessage(`Hi ${response['firstName']} ${response['lastName']}, welcome.`)
      } else {
        setAuth(false);
        setUploadResultMessage('Authentication failed.')
      }
    }).catch(error => {
      setAuth(false);
      setUploadResultMessage('There is an error during the authentication process.');
      console.error(error);
    })
  }

  async function authenticate(visitorImageName) {
    const requestUrl = `${apiGateway}/project?` + new URLSearchParams({
      objectKey: `${visitorImageName}.jpeg`
    });
    return await fetch(requestUrl, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    }).then(response => response.json()).then((data) => {
      return data;
    }).catch(error => console.error(error));
  }

  return (
    <>
    <div className="App">
      <h2>Facial with AWS.</h2>
      <form onSubmit={sendImage}>
        <input type="file" name='image' onChange={e => setImage(e.target.files[0])} />
        <button type='submit'>Authenticate</button>
      </form>
      <div className={isAuth ? 'success' : 'failure'}>{uploadResultMessage}</div>
      <img src={`/visitors/${visitorName}`} alt="Visitor" height={250} width={250}/>
    </div>
    </>
  )
}

export default App

