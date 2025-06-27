import React, { useState, useEffect } from "react";

export default function FileManager() {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);

  const fetchFiles = async () => {
    const res = await fetch("http://localhost:5000/list-files", {
      credentials: "include"
    });
    const data = await res.json();
    setFiles(data);
  };

  useEffect(() => {
    fetchFiles();
  }, []);

  const handleUpload = async e => {
    const file = e.target.files[0];
    if (!file) return;

    if (!["application/pdf", "text/plain", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"].includes(file.type)) {
      alert("Invalid file type.");
      return;
    }
    if (file.size > 20 * 1024 * 1024) {
      alert("File too large.");
      return;
    }

    const form = new FormData();
    form.append("file", file);
    setUploading(true);
    await fetch("http://localhost:5000/upload", {
      method: "POST",
      credentials: "include",
      body: form
    });
    setUploading(false);
    fetchFiles();
  };

  const handleDelete = async fn => {
    await fetch("http://localhost:5000/delete-file", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ filename: fn })
    });
    fetchFiles();
  };

  return (
    <div className="file-manager">
      <h4>Your Files</h4>
      <input type="file" onChange={handleUpload} />
      {uploading && <p>Uploading...</p>}
      <ul>
        {files.map((fn, i) => (
          <li key={i}>
            {fn}
            <button onClick={() => handleDelete(fn)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
