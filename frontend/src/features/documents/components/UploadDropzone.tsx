'use client';

import React, { useState, useCallback } from 'react';
import { Upload, FileText, X, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { clsx } from 'clsx';
import { useMutation, useQueryClient } from '@tanstack/react-query';

import { DocumentService } from '../services/document.service';
import { FILE_CONFIG } from '@/config/constants';
import { notify } from '@/lib/notifications';

/**
 * Premium Drag-and-Drop upload zone with real-time feedback.
 */
const UploadDropzone: React.FC = () => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");
  const queryClient = useQueryClient();

  const FUNNY_UPLOAD_MESSAGES = [
    "Uploading to Secure Vault...",
    "Bribing the upload gnomes...",
    "Compressing reality into a PDF...",
    "Making sure the AI has its coffee...",
    "Digitizing your thoughts...",
    "Sending to the moon and back...",
  ];

  const uploadMutation = useMutation({
    mutationFn: (file: File) => DocumentService.upload(file),
    onMutate: () => {
      setUploadMessage(FUNNY_UPLOAD_MESSAGES[Math.floor(Math.random() * FUNNY_UPLOAD_MESSAGES.length)]);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      notify.success('Document uploaded. Processing started...');
      setUploadMessage("");
    },
    onError: (error: any) => {
      notify.error(error.message || 'Upload failed');
      setUploadMessage("");
    },
  });

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
  }, []);

  const handleFiles = (files: File[]) => {
    files.forEach(file => {
      // Validation
      if (file.type !== 'application/pdf') {
        notify.error(`${file.name} is not a PDF`);
        return;
      }
      if (file.size > FILE_CONFIG.MAX_SIZE_MB * 1024 * 1024) {
        notify.error(`${file.name} exceeds ${FILE_CONFIG.MAX_SIZE_MB}MB limit`);
        return;
      }
      
      uploadMutation.mutate(file);
    });
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-4">
      <div
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={onDrop}
        className={clsx(
          "relative group cursor-pointer flex flex-col items-center justify-center p-12 border-2 border-dashed rounded-[2rem] transition-all duration-500 overflow-hidden bg-gray-900/20 backdrop-blur-sm",
          isDragging ? "border-blue-500 bg-blue-500/5 scale-[1.01]" : "border-gray-800 hover:border-gray-700 hover:bg-gray-800/20"
        )}
      >
        {/* Animated Background Orbs */}
        <div className={clsx(
          "absolute -z-10 h-64 w-64 bg-blue-600/10 blur-[100px] rounded-full transition-opacity duration-700",
          isDragging ? "opacity-100" : "opacity-0"
        )} />

        <div className={clsx(
          "mb-6 p-5 rounded-3xl transition-all duration-500 shadow-2xl",
          isDragging ? "bg-blue-600 text-white rotate-12 scale-110" : "bg-gray-800 text-gray-400 group-hover:bg-gray-700 group-hover:text-blue-400"
        )}>
          <Upload className="h-8 w-8" />
        </div>

        <div className="text-center space-y-2">
          <h3 className="text-lg font-bold text-white tracking-tight">
            {isDragging ? 'Drop to Ingest PDF' : 'Upload Research Papers'}
          </h3>
          <p className="text-sm text-gray-500 max-w-xs">
            Drag and drop your PDFs here, or click to browse. Max {FILE_CONFIG.MAX_SIZE_MB}MB.
          </p>
        </div>

        <input
          type="file"
          className="absolute inset-0 opacity-0 cursor-pointer"
          accept=".pdf"
          multiple
          onChange={(e) => handleFiles(Array.from(e.target.files || []))}
        />

        {uploadMessage && (
          <div className="absolute inset-0 bg-gray-950/60 backdrop-blur-sm flex flex-col items-center justify-center space-y-4 animate-in fade-in duration-300">
             <Loader2 className="h-10 w-10 text-blue-500 animate-spin" />
             <p className="text-sm font-medium text-blue-400">{uploadMessage}</p>
          </div>
        )}
      </div>

      <div className="mt-8 flex items-center justify-between px-2">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 text-green-500" />
            <span className="text-[11px] font-bold text-gray-500 uppercase tracking-widest">End-to-End Encrypted</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 text-green-500" />
            <span className="text-[11px] font-bold text-gray-500 uppercase tracking-widest">Semantic Indexing</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadDropzone;
