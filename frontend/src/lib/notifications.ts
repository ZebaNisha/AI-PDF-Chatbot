import toast from 'react-hot-toast';

/**
 * Centralized notification service.
 * Abstracts the toast implementation to make it easy to swap later.
 */
export const notify = {
  success: (message: string) => {
    toast.success(message, {
      duration: 4000,
      position: 'bottom-right',
      style: {
        background: '#1f2937',
        color: '#fff',
        borderRadius: '10px',
        border: '1px solid #374151',
      },
    });
  },

  error: (message: string | Error) => {
    const msg = typeof message === 'string' ? message : message.message;
    toast.error(msg, {
      duration: 6000,
      position: 'bottom-right',
      style: {
        background: '#1f2937',
        color: '#fff',
        borderRadius: '10px',
        border: '1px solid #ef4444',
      },
    });
  },

  loading: (message: string) => {
    return toast.loading(message, {
      position: 'bottom-right',
      style: {
        background: '#1f2937',
        color: '#fff',
        borderRadius: '10px',
        border: '1px solid #3b82f6',
      },
    });
  },

  dismiss: (toastId?: string) => {
    toast.dismiss(toastId);
  },
};
