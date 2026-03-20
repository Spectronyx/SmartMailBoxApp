import React, { useEffect, useState } from 'react';
import { mailboxService, emailService } from '../services/api';
import { authService } from '../services/auth';
import { Plus, RefreshCw, Trash2, Mail, RotateCcw, ShieldCheck, ShieldAlert, ExternalLink } from 'lucide-react';
import { clsx } from 'clsx';

const MailboxManager = () => {
    const [mailboxes, setMailboxes] = useState([]);
    const [loading, setLoading] = useState(true);
    const [syncing, setSyncing] = useState(null);
    const [resetting, setResetting] = useState(false);
    const [showAddForm, setShowAddForm] = useState(false);
    const [newMailbox, setNewMailbox] = useState({
        email_address: '',
        provider: 'GMAIL',
        is_active: true,
        imap_server: '',
        password: ''
    });

    const fetchMailboxes = async () => {
        try {
            setLoading(true);
            const response = await mailboxService.getAll();
            setMailboxes(response.data.results || []);
        } catch (error) {
            console.error("Failed to fetch mailboxes", error);
        } finally {
            setLoading(false);
        }
    };

    const handleGoogleConnect = async () => {
        try {
            const url = await authService.getGoogleAuthUrl();
            window.location.href = url;
        } catch (error) {
            console.error("Failed to get Google Auth URL", error);
            alert("Could not connect to Google. Check your configuration.");
        }
    };

    const handleReset = async () => {
        if (!window.confirm("This will delete ALL emails and tasks across all mailboxes. Continue?")) return;
        try {
            setResetting(true);
            const res = await emailService.clearData();
            alert(res.data.message);
            fetchMailboxes();
        } catch (error) {
            console.error("Reset failed", error);
        } finally {
            setResetting(false);
        }
    };

    useEffect(() => {
        fetchMailboxes();
    }, []);

    const handleSync = async (id) => {
        try {
            setSyncing(id);
            const res = await mailboxService.sync(id);
            alert(res.data.message);
            await fetchMailboxes();
        } catch (error) {
            console.error("Sync failed", error);
            alert(error.response?.data?.details || "Sync failed. Check credentials.");
        } finally {
            setSyncing(null);
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm("Are you sure you want to delete this mailbox?")) return;

        try {
            await mailboxService.delete(id);
            setMailboxes(mailboxes.filter(m => m.id !== id));
        } catch (error) {
            console.error("Delete failed", error);
        }
    };

    const handleAddSubmit = async (e) => {
        e.preventDefault();
        try {
            await mailboxService.create(newMailbox);
            setShowAddForm(false);
            setNewMailbox({ email_address: '', provider: 'GMAIL', is_active: true, imap_server: '', password: '' });
            fetchMailboxes();
        } catch (error) {
            console.error("Create failed", error);
            alert("Failed to create mailbox.");
        }
    };

    if (loading) return (
        <div className="flex items-center justify-center min-h-[400px]">
            <RefreshCw className="w-8 h-8 text-indigo-500 animate-spin" />
        </div>
    );

    return (
        <div className="space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Mailbox Settings</h1>
                    <p className="text-gray-500">Manage your connected email accounts and sync real messages.</p>
                </div>
                <div className="flex space-x-3">
                    <button
                        onClick={handleReset}
                        disabled={resetting}
                        className="flex items-center px-4 py-2 border border-red-200 text-red-600 rounded-lg hover:bg-red-50 transition-colors"
                    >
                        <RotateCcw className={clsx("w-4 h-4 mr-2", resetting && "animate-spin")} />
                        Reset Data
                    </button>
                    <button
                        onClick={() => setShowAddForm(!showAddForm)}
                        className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                    >
                        <Plus className="w-5 h-5 mr-1" />
                        Add Manually
                    </button>
                </div>
            </div>

            {/* Quick Connect Section */}
            {!showAddForm && (
                <div className="bg-indigo-600 rounded-xl p-6 text-white flex flex-col md:flex-row items-center justify-between gap-6">
                    <div className="flex items-center gap-4 text-center md:text-left">
                        <div className="p-3 bg-white/10 rounded-lg">
                            <Mail className="w-8 h-8" />
                        </div>
                        <div>
                            <h2 className="text-xl font-semibold">Fast Connect with Gmail</h2>
                            <p className="text-white/80">Connect your Google account to fetch real emails automatically with one click.</p>
                        </div>
                    </div>
                    <button
                        onClick={handleGoogleConnect}
                        className="whitespace-nowrap px-6 py-3 bg-white text-indigo-600 font-bold rounded-lg hover:bg-indigo-50 transition-colors flex items-center"
                    >
                        <ExternalLink className="w-5 h-5 mr-2" />
                        Sign in with Google
                    </button>
                </div>
            )}

            {showAddForm && (
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 mb-6 animate-in slide-in-from-top-2">
                    <h3 className="text-lg font-medium mb-4">Connect IMAP Account</h3>
                    <form onSubmit={handleAddSubmit} className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
                                <input
                                    type="email"
                                    required
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                                    value={newMailbox.email_address}
                                    onChange={e => setNewMailbox({ ...newMailbox, email_address: e.target.value })}
                                    placeholder="you@gmail.com"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Provider</label>
                                <select
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                                    value={newMailbox.provider}
                                    onChange={e => setNewMailbox({ ...newMailbox, provider: e.target.value })}
                                >
                                    <option value="GMAIL">Gmail</option>
                                    <option value="OUTLOOK">Outlook</option>
                                    <option value="IMAP">Custom IMAP</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">IMAP Server</label>
                                <input
                                    type="text"
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                                    value={newMailbox.imap_server}
                                    onChange={e => setNewMailbox({ ...newMailbox, imap_server: e.target.value })}
                                    placeholder="imap.gmail.com"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">App Password</label>
                                <input
                                    type="password"
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                                    value={newMailbox.password}
                                    onChange={e => setNewMailbox({ ...newMailbox, password: e.target.value })}
                                    placeholder="•••• •••• •••• ••••"
                                />
                                <p className="text-xs text-gray-400 mt-1">Use a 16-character Google App Password, not your regular password.</p>
                            </div>
                        </div>
                        <div className="flex justify-end space-x-3 pt-2">
                            <button
                                type="button"
                                onClick={() => setShowAddForm(false)}
                                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
                            >
                                Cancel
                            </button>
                            <button
                                type="submit"
                                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                            >
                                Connect IMAP
                            </button>
                        </div>
                    </form>
                </div>
            )}

            <div className="grid gap-4">
                {mailboxes.length === 0 ? (
                    <div className="text-center py-16 bg-white rounded-xl border-2 border-dashed border-gray-200">
                        <Mail className="mx-auto h-16 w-16 text-gray-300" />
                        <h3 className="mt-4 text-lg font-medium text-gray-900">No accounts connected</h3>
                        <p className="mt-2 text-gray-500 max-w-xs mx-auto">Connect your Gmail or IMAP account above to start analyzing your emails.</p>
                    </div>
                ) : (
                    mailboxes.map((mailbox) => {
                        const isConnected = mailbox.provider === 'GMAIL' || (mailbox.imap_server && mailbox.password);

                        return (
                            <div key={mailbox.id} className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                                <div className="flex items-center space-x-4">
                                    <div className={clsx(
                                        "h-12 w-12 rounded-full flex items-center justify-center font-bold",
                                        isConnected ? "bg-indigo-100 text-indigo-600" : "bg-gray-100 text-gray-400"
                                    )}>
                                        {mailbox.provider[0]}
                                    </div>
                                    <div className="min-w-0">
                                        <h3 className="text-lg font-medium text-gray-900 truncate">{mailbox.email_address}</h3>
                                        <div className="flex items-center mt-1">
                                            {isConnected ? (
                                                <span className="flex items-center text-xs text-green-600 font-medium">
                                                    <ShieldCheck className="w-3 h-3 mr-1" />
                                                    Connected ({mailbox.provider})
                                                </span>
                                            ) : (
                                                <span className="flex items-center text-xs text-amber-600 font-medium">
                                                    <ShieldAlert className="w-3 h-3 mr-1" />
                                                    Demo Mode (No Credentials)
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                </div>

                                <div className="flex items-center justify-between sm:justify-end gap-3 pt-4 sm:pt-0 border-t sm:border-t-0 border-gray-50">
                                    <div className="text-right hidden sm:block mr-4">
                                        <p className="text-[10px] text-gray-400 uppercase font-bold tracking-wider">Last Sync</p>
                                        <p className="text-xs text-gray-600">{mailbox.last_synced_at ? new Date(mailbox.last_synced_at).toLocaleTimeString() : 'Never'}</p>
                                    </div>

                                    <button
                                        onClick={() => handleSync(mailbox.id)}
                                        disabled={syncing === mailbox.id}
                                        className={clsx(
                                            "flex items-center px-3 py-2 rounded-lg text-sm transition-all",
                                            syncing === mailbox.id
                                                ? "bg-indigo-50 text-indigo-600 cursor-not-allowed"
                                                : "text-indigo-600 hover:bg-indigo-50 border border-indigo-100"
                                        )}
                                    >
                                        <RefreshCw className={clsx("w-4 h-4 mr-2", syncing === mailbox.id && "animate-spin")} />
                                        {syncing === mailbox.id ? 'Syncing...' : 'Sync Now'}
                                    </button>
                                    <button
                                        onClick={() => handleDelete(mailbox.id)}
                                        className="p-2 rounded-lg text-gray-400 hover:bg-red-50 hover:text-red-500 transition-colors"
                                        title="Remove Account"
                                    >
                                        <Trash2 className="w-5 h-5" />
                                    </button>
                                </div>
                            </div>
                        );
                    })
                )}
            </div>
        </div>
    );
};

export default MailboxManager;
