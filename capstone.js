const express = require('express');
const app = express();
const fs = require('fs');
const path = require('path');

app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Content-Type');
  res.header('Cache-Control', 'max-age=60');
  next();
});

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'web.html'));
});

app.get('*', (req, res) => {
  const filePath = path.join(__dirname, req.url);

  if (req.url === '/files') {
    const folderPath = '파일경로';
    fs.readdir(folderPath, (err, files) => {
      if (err) {
        console.error(err);
        return res.status(500).send('Internal Server Error');
      }
      res.json(files);
    });
  } else {
    fs.readFile(filePath, 'utf-8', (err, data) => {
      if (err) {
        res.statusCode = 500;
        res.end('Internal Server Error');
      } else {
        let contentType = 'text/plain';
        if (filePath.endsWith('.html')) {
          contentType = 'text/html';
        } else if (filePath.endsWith('.js')) {
          contentType = 'application/javascript';
        }

        res.writeHead(200, {
          'Content-Type': contentType
        });
        res.end(data);
      }
    });
  }
});

const PORT = 3050;
app.listen(PORT, () => {
  console.log(`Server is listening on port ${PORT}`);
});
