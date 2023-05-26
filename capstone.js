const express = require('express');
const cors = require('cors');
const { exec } = require('child_process');
const app = express();
const fs = require('fs');
const path = require('path');
app.use(cors());
app.use('/models', express.static('models'));
app.use(express.json());
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'webb.html'));
});

app.get('/load_obj.html', (req, res) => {
  res.sendFile(path.join(__dirname, 'load_obj.html'));
});

app.get('/files', (req, res) => {
  const folderPath = 'C:/Users/ESE/Desktop/capstone/models';
  fs.readdir(folderPath, (err, files) => {
    if (err) {
      console.error(err);
      return res.status(500).send('Internal Server Error');
    }
    res.json(files);
  });
});


app.post('/execute-script', (req, res) => {
  const fileName = req.body.fileName;
  const scriptPath = `C:/Users/ESE/Desktop/capstone/models`;
  const command = `cd "${scriptPath}" && instant-ngp ${fileName}`;
  console.log(`Script output: ${fileName}`);
  exec(command, (error, stdout, stderr) => {
    if (error) {
      console.error(`Error executing script: ${error.message}`);
      return res.status(500).send('Error executing script');
    }
    console.log(`Script output: ${stdout} and ${fileName}`);

  });
});
const PORT = 3050;
app.listen(PORT, () => {
  console.log(`Server is listening on port ${PORT}`);
});
