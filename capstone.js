const express = require('express');
const app = express();
const fs = require('fs');
const path = require('path');

app.use('/models', express.static('models'));

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});
app.get('/objj.html', (req, res) => {
  res.sendFile(path.join(__dirname, 'objj.html'));
});

app.get('/files', (req, res) => {
  const folderPath = 'C:/Users/ESE/Desktop/capstone/models';
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
