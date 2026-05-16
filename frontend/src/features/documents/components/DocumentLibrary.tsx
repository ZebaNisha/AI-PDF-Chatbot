'use client';

import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { FileText, Trash2, Clock, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { Document, DocumentStatus } from '@/types';
import { DocumentService } from '../services/document.service';
import { notify } from '@/lib/notifications';
import { clsx } from 'clsx';

/**
 * Visual progress indicator for document processing stages.
 */
const StatusIndicator: React.FC<{ status: DocumentStatus }> = ({ status }) => {
  const config = {
    [DocumentStatus.PENDING]: { icon: Clock, color: 'bg-gray-700', text: 'text-gray-400', label: 'In Queue', percent: 5 },
    [DocumentStatus.UPLOADED]: { icon: Loader2, color: 'bg-blue-600', text: 'text-blue-400', label: 'Uploaded', percent: 15 },
    [DocumentStatus.EXTRACTING]: { icon: Loader2, color: 'bg-purple-600', text: 'text-purple-400', label: 'Reading PDF...', percent: 30 },
    [DocumentStatus.CHUNKING]: { icon: Loader2, color: 'bg-indigo-600', text: 'text-indigo-400', label: 'Dicing Content...', percent: 50 },
    [DocumentStatus.EMBEDDING]: { icon: Loader2, color: 'bg-cyan-600', text: 'text-cyan-400', label: 'Generating AI Brain...', percent: 70 },
    [DocumentStatus.STORING]: { icon: Loader2, color: 'bg-sky-600', text: 'text-sky-400', label: 'Storing Memories...', percent: 90 },
    [DocumentStatus.COMPLETED]: { icon: CheckCircle, color: 'bg-green-600', text: 'text-green-400', label: 'Ready to Chat!', percent: 100 },
    [DocumentStatus.FAILED]: { icon: AlertCircle, color: 'bg-red-600', text: 'text-red-400', label: 'Extraction Failed', percent: 100 },
  }[status];

  const Icon = config.icon;
  const isProcessing = ![DocumentStatus.COMPLETED, DocumentStatus.FAILED, DocumentStatus.PENDING].includes(status);

  return (
    <div className="flex flex-col items-end gap-2 min-w-[140px]">
      <div className="flex items-center gap-2">
        <Icon className={clsx("h-3 w-3", config.text, isProcessing && "animate-spin")} />
        <span className={clsx("text-[10px] font-bold uppercase tracking-wider", config.text)}>
          {config.label}
        </span>
      </div>
      <div className="w-full h-1.5 bg-gray-800 rounded-full overflow-hidden">
        <div 
          className={clsx("h-full transition-all duration-1000 ease-out", config.color)}
          style={{ width: `${config.percent}%` }}
        />
      </div>
    </div>
  );
};


const DocumentLibrary: React.FC = () => {
  const queryClient = useQueryClient();
  
  const { data: documents, isLoading } = useQuery<Document[]>({
    queryKey: ['documents'],
    queryFn: () => DocumentService.list(),
    refetchInterval: (query) => {
      const docs = query.state.data as Document[] | undefined;
      const isProcessing = docs?.some(d => 
        ![DocumentStatus.COMPLETED, DocumentStatus.FAILED].includes(d.status)
      );
      return isProcessing ? 3000 : false;
    }
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => DocumentService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      notify.success('Document deleted');
    },
    onError: (error: any) => notify.error(error.message || 'Delete failed'),
  });

  if (isLoading) return (
    <div className="flex flex-col items-center justify-center p-20 opacity-50">
      <Loader2 className="h-8 w-8 animate-spin mb-4" />
      <p className="text-sm font-mono text-gray-500 uppercase tracking-widest">Fetching Library...</p>
    </div>
  );

  if (!documents?.length) return (
    <div className="flex flex-col items-center justify-center p-20 text-center bg-gray-900/10 border border-dashed border-gray-800 rounded-[2rem]">
       <div className="h-16 w-16 bg-gray-800/50 rounded-2xl flex items-center justify-center mb-6">
          <FileText className="h-8 w-8 text-gray-700" />
       </div>
       <h3 className="text-white font-bold mb-2">No Documents Found</h3>
       <p className="text-sm text-gray-500 max-w-xs mx-auto">
         Your knowledge base is empty. Upload a PDF to start chatting with your data.
       </p>
    </div>
  );

  return (
    <div className="w-full max-w-4xl mx-auto space-y-3">
      {documents.map((doc) => (
        <div 
          key={doc.id}
          className="group flex items-center justify-between p-4 bg-gray-900/30 hover:bg-gray-900/50 border border-gray-800 hover:border-gray-700 rounded-2xl transition-all duration-300"
        >
          <div className="flex items-center gap-4">
            <div className="h-10 w-10 bg-gray-800/50 rounded-xl flex items-center justify-center text-gray-400 group-hover:text-blue-400 transition-colors">
              <FileText className="h-5 w-5" />
            </div>
            <div>
              <h4 className="text-sm font-semibold text-gray-200 group-hover:text-white transition-colors">{doc.original_filename}</h4>
              <div className="flex items-center gap-3 mt-1">
                <span className="text-[10px] text-gray-500 font-mono">{(doc.file_size / (1024 * 1024)).toFixed(2)} MB</span>
                <span className="text-gray-700">•</span>
                <span className="text-[10px] text-gray-500 font-mono">Added {new Date(doc.created_at).toLocaleDateString()}</span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-6">
            <StatusIndicator status={doc.status} />
            
            <button
              onClick={() => {
                if (window.confirm('Delete this document and all associated data?')) {
                  deleteMutation.mutate(doc.id);
                }
              }}
              className="p-2 text-gray-600 hover:text-red-500 hover:bg-red-500/10 rounded-lg transition-all"
              disabled={deleteMutation.isPending}
            >
              <Trash2 className="h-4 w-4" />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};

export default DocumentLibrary;
