import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import api from '../services/api';
import { authService } from '../services/auth';


const GoogleCallback = () => {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        const finalizeGoogleAuth = async () => {
            const queryParams = new URLSearchParams(location.search);
            const code = queryParams.get('code');

            if (!code) {
                setError('No authorization code received from Google.');
                setLoading(false);
                return;
            }

            try {
                const response = await api.get(`/auth/google/callback/?code=${code}`);


                console.log('Google Auth success:', response.data);
                navigate('/mailboxes', { state: { message: 'Google account linked successfully!' } });
            } catch (err) {
                setError(err.response?.data?.error || 'Failed to complete Google authentication.');
            } finally {
                setLoading(false);
            }
        };

        finalizeGoogleAuth();
    }, [location, navigate]);

    return (
        <div className="flex flex-col items-center justify-center min-h-[60vh] text-white">
            <div className="p-8 bg-gray-800 rounded-2xl shadow-2xl border border-gray-700 max-w-md w-full text-center">
                {loading ? (
                    <>
                        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto mb-4"></div>
                        <h2 className="text-xl font-bold">Connecting your Gmail...</h2>
                        <p className="text-gray-400 mt-2">Almost there, just finalizing the secure link.</p>
                    </>
                ) : error ? (
                    <>
                        <div className="text-red-500 text-5xl mb-4">⚠️</div>
                        <h2 className="text-xl font-bold text-red-400">Authentication Failed</h2>
                        <p className="text-gray-400 mt-2">{error}</p>
                        <button
                            onClick={() => navigate('/login')}
                            className="mt-6 py-2 px-6 bg-gray-700 hover:bg-gray-600 rounded-lg transition"
                        >
                            Back to Login
                        </button>
                    </>
                ) : (
                    <div className="text-green-500 font-bold">Redirecting...</div>
                )}
            </div>
        </div>
    );
};

export default GoogleCallback;
