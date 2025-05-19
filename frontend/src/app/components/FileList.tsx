'use client';

import { useEffect, useState } from 'react';
import { format } from 'date-fns';
import { Download, Eye, AlertCircle, CheckCircle, Clock } from 'lucide-react';

interface File {
  id: number;
  filename: string;
  content_type: string;
  upload_time: string;
  path: string;
  converted_pptx_path: string | null;
  conversion_status: string;
}

interface FileListProps {
  files: File[];
}

export default function FileList({ files }: FileListProps) {
  if (files.length === 0) return <div className="text-center py-4">No files uploaded yet</div>;

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const getStatusIcon = (status: string) => {
    if (status === 'success') return <CheckCircle className="w-5 h-5 text-green-500" />;
    if (status === 'pending') return <Clock className="w-5 h-5 text-yellow-500" />;
    if (status === 'not_applicable') return null;
    return <AlertCircle className="w-5 h-5 text-red-500" />;
  };

  const getStatusText = (status: string) => {
    if (status === 'success') return 'Converted';
    if (status === 'pending') return 'Converting...';
    if (status === 'not_applicable') return 'Not applicable';
    return `Failed: ${status.replace('failed: ', '')}`;
  };

  const handleDownload = async (fileId: number, filename: string, isPptx: boolean = false) => {
    const endpoint = isPptx
      ? `${apiUrl}/api/v1/files/download-pptx/${fileId}`
      : `${apiUrl}/api/v1/files/download/${fileId}`;
    try {
      const response = await fetch(endpoint, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (!response.ok) throw new Error('Failed to download file');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert('Download failed: ' + (err instanceof Error ? err.message : 'Unknown error'));
    }
  };

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Your Files</h2>
      <div className="grid gap-4">
        {files.map((file) => (
          <div
            key={file.id}
            className="bg-white p-4 rounded-lg shadow border border-gray-200"
          >
            <div className="flex items-center justify-between">
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {file.filename}
                </p>
                <p className="text-sm text-gray-500">
                  Uploaded {format(new Date(file.upload_time), 'PPp')}
                </p>
              </div>
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  {getStatusIcon(file.conversion_status)}
                  <span className="text-sm text-gray-600">
                    {getStatusText(file.conversion_status)}
                  </span>
                </div>
                <div className="flex space-x-2">
                  {/* Download original file */}
                  <button
                    onClick={() => handleDownload(file.id, file.filename)}
                    className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-full"
                    title="Download original file"
                  >
                    <Download className="w-5 h-5" />
                  </button>
                  {/* Preview/download converted PPTX if available */}
                  {file.converted_pptx_path && file.conversion_status === 'success' && (
                    <button
                      onClick={() => handleDownload(file.id, file.filename.endsWith('.pptx') ? file.filename : file.filename.replace(/\.[^.]+$/, '.pptx'), true)}
                      className="p-2 text-blue-600 hover:text-blue-900 hover:bg-blue-50 rounded-full"
                      title="View converted presentation"
                    >
                      <Eye className="w-5 h-5" />
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}