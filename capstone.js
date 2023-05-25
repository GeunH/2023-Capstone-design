const express = require('express');
const cors = require('cors');
const { exec } = require('child_process');
const app = express();
const fs = require('fs');
const path = require('path');
app.use(cors());
app.use('/models', express.static('models'));

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


app.get('/execute-script', (req, res) => {
  exec('cd "C:/Users/ESE/Desktop/Instant-NGP-for-GTX-1000" && instant-ngp RACKA_SAM_base.ingp', (error, stdout, stderr) => {
    if (error) {
      console.error(`Error executing script: ${error.message}`);
      return res.status(500).send('Error executing script');
    }
    console.log(`Script output: ${stdout}`);

    const executionDataFilePath = 'executionData.txt';
    fs.writeFile(executionDataFilePath, stdout, (err) => {
      if (err) {
        console.error(`Error saving execution data: ${err.message}`);
        return res.status(500).send('Error saving execution data');
      }
      console.log('Execution data saved successfully');

      // 클라이언트에 GUI 데이터 파일의 URL을 전달
      const guiDataFileURL = `http://192.168.0.59/executionData.txt`;
      res.send({ url: guiDataFileURL });
    });
  });
});
const PORT = 3040;
app.listen(PORT, () => {
  console.log(`Server is listening on port ${PORT}`);
});
