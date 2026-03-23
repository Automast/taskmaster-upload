const express = require('express');
const cors = require('cors');
const multer = require('multer');
const fs = require('fs');
const path = require('path');

const app = express();
const port = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

const UPLOAD_DIR = path.join(__dirname, 'uploads');
if (!fs.existsSync(UPLOAD_DIR)) {
    fs.mkdirSync(UPLOAD_DIR, { recursive: true });
}

// Serve uploaded files statically so any frontend can use them
app.use('/data', express.static(UPLOAD_DIR));

const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        let folderName = req.body.folderName || 'default';
        // sanitize foldername to prevent path traversal
        folderName = path.basename(folderName);
        const folderPath = path.join(UPLOAD_DIR, folderName);
        if (!fs.existsSync(folderPath)) {
            fs.mkdirSync(folderPath, { recursive: true });
        }
        cb(null, folderPath);
    },
    filename: (req, file, cb) => {
        let folderName = req.body.folderName || 'default';
        folderName = path.basename(folderName);
        const folderPath = path.join(UPLOAD_DIR, folderName);
        
        let originalName = file.originalname;
        let ext = path.extname(originalName);
        let baseName = path.basename(originalName, ext);
        
        let newName = originalName;
        let counter = 1;
        
        // Handle name collision
        while (fs.existsSync(path.join(folderPath, newName))) {
            newName = `${baseName}_${counter}${ext}`;
            counter++;
        }
        
        cb(null, newName);
    }
});

const upload = multer({ storage: storage });

app.post('/upload', upload.single('file'), (req, res) => {
    if (!req.file) {
        return res.status(400).json({ error: 'No file uploaded' });
    }
    res.json({ message: 'File uploaded successfully', filename: req.file.filename });
});

app.get('/folders', (req, res) => {
    try {
        const items = fs.readdirSync(UPLOAD_DIR);
        const folders = [];
        for (const item of items) {
            const folderPath = path.join(UPLOAD_DIR, item);
            const stat = fs.statSync(folderPath);
            if (stat.isDirectory()) {
                const files = fs.readdirSync(folderPath).filter(f => fs.statSync(path.join(folderPath, f)).isFile());
                folders.push({ name: item, files: files });
            }
        }
        res.json({ folders });
    } catch (err) {
        res.status(500).json({ error: 'Failed to list folders' });
    }
});

app.delete('/folders/:folderName', (req, res) => {
    const folderName = path.basename(req.params.folderName);
    const folderPath = path.join(UPLOAD_DIR, folderName);
    
    if (fs.existsSync(folderPath)) {
        try {
            const files = fs.readdirSync(folderPath);
            for (const file of files) {
                fs.unlinkSync(path.join(folderPath, file));
            }
            res.json({ message: `All files in '${folderName}' deleted successfully` });
        } catch (err) {
            res.status(500).json({ error: 'Failed to delete files' });
        }
    } else {
        res.status(404).json({ error: 'Folder not found' });
    }
});

app.delete('/folders/:folderName/files/:fileName', (req, res) => {
    const folderName = path.basename(req.params.folderName);
    const fileName = path.basename(req.params.fileName);
    const filePath = path.join(UPLOAD_DIR, folderName, fileName);
    
    if (fs.existsSync(filePath)) {
        try {
            fs.unlinkSync(filePath);
            res.json({ message: `File '${fileName}' deleted successfully` });
        } catch (err) {
            res.status(500).json({ error: 'Failed to delete file' });
        }
    } else {
        res.status(404).json({ error: 'File not found' });
    }
});

// A simple root endpoint
app.get('/', (req, res) => {
    res.send('Video Upload Server is running!');
});

app.listen(port, () => {
    console.log(`Server listening at http://localhost:${port}`);
});
