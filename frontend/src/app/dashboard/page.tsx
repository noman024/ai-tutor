'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';

export default function DashboardPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');
  const [uploadSuccess, setUploadSuccess] = useState('');
  const [files, setFiles] = useState<File[]>([]);
  const [uploadedFiles, setUploadedFiles] = useState<any[]>([]);
  const [loadingFiles, setLoadingFiles] = useState(false);

  const fetchUploadedFiles = useCallback(async () => {
    setLoadingFiles(true);
    try {
      const token = localStorage.getItem('token');
      const res = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/files/list`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      setUploadedFiles(res.data);
    } catch {
      setUploadedFiles([]);
    } finally {
      setLoadingFiles(false);
    }
  }, []);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
    } else {
      fetchUploadedFiles();
    }
  }, [router, fetchUploadedFiles]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFiles(e.target.files ? Array.from(e.target.files) : []);
    setUploadError('');
    setUploadSuccess('');
  };

  const handleDrop = (e: React.DragEvent<HTMLLabelElement>) => {
    e.preventDefault();
    setFiles(Array.from(e.dataTransfer.files));
    setUploadError('');
    setUploadSuccess('');
  };

  const handleDragOver = (e: React.DragEvent<HTMLLabelElement>) => {
    e.preventDefault();
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    setUploadError('');
    setUploadSuccess('');
    if (!files.length) {
      setUploadError('Please select at least one file.');
      return;
    }
    setUploading(true);
    try {
      const formData = new FormData();
      files.forEach(file => formData.append('uploads', file));
      const token = localStorage.getItem('token');
      await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/files/upload`,
        formData,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      setUploadSuccess('File(s) uploaded successfully!');
      setFiles([]);
      fetchUploadedFiles();
    } catch (err: any) {
      setUploadError(err.response?.data?.detail || 'File upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <div className="bg-white p-8 rounded shadow-md w-full max-w-md text-center">
        <h2 className="text-2xl font-bold mb-4">Dashboard</h2>
        <p className="mb-4">You are logged in!</p>
        <button
          className="btn-secondary"
          onClick={() => {
            localStorage.removeItem('token');
            router.push('/login');
          }}
        >
          Logout
        </button>
        <form onSubmit={handleUpload} className="mb-4 flex flex-col items-center space-y-4 w-full">
          <label
            className="w-full flex flex-col items-center px-4 py-6 bg-white text-blue-600 rounded-lg shadow-md tracking-wide uppercase border-2 border-dashed border-blue-200 cursor-pointer hover:bg-blue-50 transition-colors"
            onDrop={handleDrop}
            onDragOver={handleDragOver}
          >
            <svg className="w-8 h-8" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M7 10l5-5m0 0l5 5m-5-5v12"></path></svg>
            <span className="mt-2 text-base leading-normal">
              {files.length > 0 ? files.map(f => f.name).join(', ') : 'Drag & drop or click to select files'}
            </span>
            <input
              type="file"
              onChange={handleFileChange}
              className="hidden"
              disabled={uploading}
              multiple
              accept=".pdf,.doc,.docx,.ppt,.pptx,.jpg,.jpeg,.png"
            />
          </label>
          <button
            type="submit"
            className="btn-primary w-full rounded-full py-2 text-lg"
            disabled={uploading}
          >
            {uploading ? 'Uploading...' : 'Upload File(s)'}
          </button>
          {uploadError && <div className="text-red-600 text-sm flex items-center"><svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12"></path></svg>{uploadError}</div>}
          {uploadSuccess && <div className="text-green-600 text-sm flex items-center"><svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7"></path></svg>{uploadSuccess}</div>}
        </form>
        <div className="w-full mt-6">
          <h3 className="text-lg font-semibold mb-2 text-left">Your Uploaded Files</h3>
          {loadingFiles ? (
            <div>Loading...</div>
          ) : uploadedFiles.length === 0 ? (
            <div className="text-gray-500">No files uploaded yet.</div>
          ) : (
            <ul className="divide-y divide-gray-200">
              {uploadedFiles.map(file => (
                <li key={file.id} className="py-2 flex items-center justify-between">
                  <span className="truncate max-w-xs" title={file.filename}>{file.filename}</span>
                  <span className="text-xs text-gray-400 ml-2">{new Date(file.upload_time).toLocaleString()}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
} 