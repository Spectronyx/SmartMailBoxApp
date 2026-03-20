import React, { useEffect, useState } from 'react';
import { Plus, RefreshCw, Trash2, Mail } from 'lucide-react';
import { mailboxService } from '../services/api';
import { authService } from '../services/auth';
import { formatDistanceToNow } from 'date-fns';
import { clsx } from 'clsx';

const MailboxManager = () => {
    const [mailboxes, setMailboxes] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showConnectModal, setShowConnectModal] = useState(false);
    const [imapData, setImapData] = useState({
        email: '',
        password: ''
    });

    const [syncInterval, setSyncInterval] = useState(5);
    const [updatingInterval, setUpdatingInterval] = useState(false);

    const fetchMailboxes = async () => {
        try {
            setLoading(true);
            const [mbRes, settingsRes] = await Promise.all([
                mailboxService.getAll(),
                mailboxService.getSyncSettings().catch(() => ({ data: { interval_minutes: 5 } }))
            ]);
            setMailboxes(mbRes.data.results || []);
            setSyncInterval(settingsRes.data.interval_minutes);
        } catch (error) {
            console.error("Failed to fetch mailboxes", error);
        } finally {
            setLoading(false);
        }
    };

    const handleUpdateInterval = async (val) => {
        try {
            setUpdatingInterval(true);
            await mailboxService.updateSyncSettings(val);
            setSyncInterval(val);
        } catch (error) {
            console.error("Failed to update interval", error);
            alert("Failed to update sync frequency.");
        } finally {
            setUpdatingInterval(false);
        }
    };

    const handleGoogleConnect = async () => {
        try {
            const url = await authService.getGoogleAuthUrl();
            window.location.href = url;
        } catch (error) {
            console.error("Failed to get Google Auth URL", error);
        }
    };

    const handleImapConnect = async () => {
        try {
            await mailboxService.connectImap(imapData);
            setShowConnectModal(false);
            setImapData({ email: '', password: '' });
            fetchMailboxes();
        } catch (error) {
            console.error("Failed to connect IMAP", error);
            alert("Failed to connect account. Please check your credentials.");
        }
    };

    const handleDelete = async (id) => {
        if (window.confirm("Are you sure you want to remove this mailbox?")) {
            try {
                await mailboxService.delete(id);
                fetchMailboxes();
            } catch (error) {
                console.error("Failed to delete mailbox", error);
            }
        }
    };

    const handleSync = async (id) => {
        try {
            await mailboxService.sync(id);
            alert("Sync started successfully!");
            fetchMailboxes();
        } catch (error) {
            console.error("Sync failed", error);
        }
    };

    useEffect(() => {
        fetchMailboxes();
    }, []);

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Mailbox Settings</h1>
                <button 
                  onClick={() => setShowConnectModal(true)}
                  className="flex items-center px-4 py-2 bg-indigo-600 dark:bg-indigo-500 text-white rounded-lg hover:bg-indigo-700 dark:hover:bg-indigo-600 shadow-sm transition-all transform active:scale-95"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add Account
                </button>
            </div>

            {/* Global Sync Settings */}
            <div className="bg-white dark:bg-gray-900 p-6 rounded-xl shadow-sm border border-gray-100 dark:border-gray-800 flex flex-col md:flex-row md:items-center justify-between gap-4 transition-all duration-300">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-indigo-50 dark:bg-indigo-900/30 rounded-lg">
                        <RefreshCw className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                    </div>
                    <div>
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Background Sync Frequency</h3>
                        <p className="text-sm text-gray-500 dark:text-gray-400">How often should the system automatically check for new mail?</p>
                    </div>
                </div>
                <div className="flex items-center gap-3">
                    <select 
                        value={syncInterval}
                        onChange={(e) => handleUpdateInterval(parseInt(e.target.value))}
                        disabled={updatingInterval}
                        className={clsx(
                            "px-4 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg font-medium text-gray-700 dark:text-gray-200 focus:ring-2 focus:ring-indigo-500 outline-none transition-all",
                            updatingInterval && "opacity-50 cursor-wait"
                        )}
                    >
                        <option value={1}>Every 1 Minute</option>
                        <option value={5}>Every 5 Minutes</option>
                        <option value={15}>Every 15 Minutes</option>
                        <option value={30}>Every 30 Minutes</option>
                        <option value={60}>Every 1 Hour</option>
                    </select>
                    {updatingInterval && <RefreshCw className="w-4 h-4 animate-spin text-indigo-600" />}
                </div>
            </div>

            <div className="grid gap-4">
                {mailboxes.length === 0 ? (
                    <div className="text-center py-16 bg-white dark:bg-gray-900 rounded-xl border-2 border-dashed border-gray-200 dark:border-gray-800">
                        <Mail className="mx-auto h-12 w-12 text-gray-400 dark:text-gray-600" />
                        <h3 className="mt-2 text-sm font-semibold text-gray-900 dark:text-gray-100">No mailboxes connected</h3>
                        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Get started by connecting your first email account.</p>
                    </div>
                ) : (
                    mailboxes.map((mailbox) => (
                        <div key={mailbox.id} className="bg-white dark:bg-gray-900 p-5 rounded-xl shadow-sm border border-gray-100 dark:border-gray-800 flex items-center justify-between transition-all duration-300">
                            <div className="flex items-center space-x-4">
                                <div className="p-3 bg-gray-100 dark:bg-gray-800 rounded-full">
                                    <Mail className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
                                </div>
                                <div className="min-w-0">
                                    <h3 className="text-base font-bold text-gray-900 dark:text-gray-100 truncate">{mailbox.email_address}</h3>
                                    <p className="text-sm text-gray-400 dark:text-gray-500 flex items-center mt-0.5">
                                        <span className="capitalize">{mailbox.provider}</span>
                                        <span className="mx-2">•</span>
                                        {mailbox.last_synced_at ? `${formatDistanceToNow(new Date(mailbox.last_synced_at))} ago` : 'Never synced'}
                                    </p>
                                </div>
                            </div>
                            <div className="flex items-center space-x-2 flex-shrink-0">
                                <button 
                                  onClick={() => handleSync(mailbox.id)}
                                  className="p-2 text-gray-400 dark:text-gray-500 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-900/30 rounded-lg transition-colors"
                                  title="Force Sync"
                                >
                                  <RefreshCw className="w-5 h-5" />
                                </button>
                                <button 
                                  onClick={() => handleDelete(mailbox.id)}
                                  className="p-2 text-gray-400 dark:text-gray-500 hover:text-red-600 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-lg transition-colors"
                                  title="Remove Account"
                                >
                                  <Trash2 className="w-5 h-5" />
                                </button>
                            </div>
                        </div>
                    ))
                )}
            </div>

            {/* Connect Modal */}
            {showConnectModal && (
                <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-gray-900/60 dark:bg-black/80 backdrop-blur-sm">
                    <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl w-full max-w-md border border-gray-100 dark:border-gray-800 overflow-hidden">
                        <div className="px-6 py-5 border-b border-gray-100 dark:border-gray-800 flex items-center justify-between">
                            <h2 className="text-xl font-bold dark:text-white tracking-tight">Add Account</h2>
                            <button 
                                onClick={() => setShowConnectModal(false)}
                                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
                            >
                                <Plus className="w-6 h-6 rotate-45" />
                            </button>
                        </div>
                        
                        <div className="p-6 space-y-6">
                            <button
                                onClick={handleGoogleConnect}
                                className="w-full flex items-center justify-center space-x-3 px-4 py-3 border-2 border-gray-100 dark:border-gray-800 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-800 font-bold text-gray-700 dark:text-gray-200 transition-all active:scale-[0.98]"
                            >
                                <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" className="w-5 h-5" alt="Google" />
                                <span>Connect with Gmail</span>
                            </button>

                            <div className="relative">
                                <div className="absolute inset-0 flex items-center"><span className="w-full border-t border-gray-100 dark:border-gray-800"></span></div>
                                <div className="relative flex justify-center text-xs uppercase font-black tracking-widest"><span className="bg-white dark:bg-gray-900 px-4 text-gray-400 dark:text-gray-500">Or IMAP</span></div>
                            </div>

                            <div className="space-y-4">
                                <input
                                    type="email"
                                    placeholder="Email Address"
                                    className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-800 border-none rounded-xl focus:ring-2 focus:ring-indigo-500 dark:text-gray-100 outline-none transition-all placeholder:text-gray-400 dark:placeholder:text-gray-600"
                                    value={imapData.email}
                                    onChange={(e) => setImapData({...imapData, email: e.target.value})}
                                />
                                <input
                                    type="password"
                                    placeholder="App Password"
                                    className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-800 border-none rounded-xl focus:ring-2 focus:ring-indigo-500 dark:text-gray-100 outline-none transition-all placeholder:text-gray-400 dark:placeholder:text-gray-600"
                                    value={imapData.password}
                                    onChange={(e) => setImapData({...imapData, password: e.target.value})}
                                />
                                <button
                                    onClick={handleImapConnect}
                                    className="w-full px-4 py-3 bg-indigo-600 dark:bg-indigo-500 text-white rounded-xl font-bold hover:bg-indigo-700 dark:hover:bg-indigo-600 shadow-lg shadow-indigo-200 dark:shadow-none transition-all active:scale-[0.98]"
                                >
                                    Connect IMAP Account
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default MailboxManager;
