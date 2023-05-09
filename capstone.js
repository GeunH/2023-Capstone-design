const express = require('express');
const app = express();
const fs = require('fs');
const path = require('path');

app.use('/models', express.static('models'));

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'web.html'));
});
app.get('/load_obj.html', (req, res) => {
  res.sendFile(path.join(__dirname, 'load_obj.html'));
});

app.get('/files', (req, res) => {
  const folderPath = 'obj파일이 담긴 폴더의 경로';
  fs.readdir(folderPath, (err, files) => {
    if (err) {
      console.error(err);
      return res.status(500).send('Internal Servererer Error');
    }
    res.json(files);
  });
});

const PORT = 3050;
app.listen(PORT, () => {
  console.log(`Server is listening on port ${PORT}`);
});
