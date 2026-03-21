import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { emailService } from '../services/api';
import { 
  ArrowLeft, 
  Sparkles, 
  CheckSquare, 
  Clock, 
  User, 
  Paperclip, 
  Archive, 
  Trash2, 
  Mail, 
  MoreVertical, 
  CornerUpLeft, 
  CornerUpRight,
  Star,
  Info
} from 'lucide-react';
import { format } from 'date-fns';
import { clsx } from 'clsx';
import { motion, AnimatePresence } from 'framer-motion';

const EmailDetail = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [email, setEmail] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchEmail = async () => {
            try {
                setLoading(true);
                const response = await emailService.get(id);
                setEmail(response.data);
            } catch (error) {
                console.error("Failed to fetch email", error);
                alert("Could not load email.");
                navigate('/inbox');
            } finally {
                setLoading(false);
            }
        };

        fetchEmail();
    }, [id, navigate]);

    const handleToggleComplete = async (taskId, currentStatus) => {
        try {
            setEmail(prev => ({
                ...prev,
                tasks: prev.tasks.map(t => 
                    t.id === taskId ? { ...t, is_completed: !currentStatus } : t
                ).sort((a, b) => (a.is_completed === b.is_completed ? 0 : a.is_completed ? 1 : -1))
            }));
            const { taskService } = await import('../services/api');
            await taskService.update(taskId, { is_completed: !currentStatus });
        } catch (error) {
            console.error("Failed to toggle task", error);
            const response = await emailService.get(id);
            setEmail(response.data);
        }
    };

    if (loading) return (
        <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-indigo-600"></div>
        </div>
    );
    if (!email) return null;

    return (
        <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex flex-col h-full bg-white dark:bg-gray-950 transition-colors duration-300 -m-4 md:-m-8"
        >
            {/* Top Gmail-style Action Bar */}
            <div className="sticky top-0 z-20 flex items-center justify-between px-4 py-2 bg-white/80 dark:bg-gray-950/80 backdrop-blur-md border-b border-gray-100 dark:border-gray-800">
                <div className="flex items-center space-x-1">
                    <button 
                        onClick={() => navigate('/inbox')}
                        className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors text-gray-600 dark:text-gray-400"
                        title="Back to Inbox"
                    >
                        <ArrowLeft className="w-5 h-5" />
                    </button>
                    <div className="h-6 w-px bg-gray-200 dark:bg-gray-800 mx-2" />
                    <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors text-gray-500" title="Archive"><Archive className="w-5 h-5" /></button>
                    <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors text-gray-500" title="Report Spam"><Info className="w-5 h-5" /></button>
                    <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors text-gray-500" title="Delete"><Trash2 className="w-5 h-5" /></button>
                    <div className="h-6 w-px bg-gray-200 dark:bg-gray-800 mx-2" />
                    <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors text-gray-500" title="Mark as Unread"><Mail className="w-5 h-5" /></button>
                    <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors text-gray-500" title="Snooze"><Clock className="w-5 h-5" /></button>
                </div>
                <div className="flex items-center">
                   <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors text-gray-500"><MoreVertical className="w-5 h-5" /></button> 
                </div>
            </div>

            <div className="flex flex-1 overflow-hidden">
                {/* Main Email Content */}
                <div className="flex-1 overflow-y-auto p-6 md:p-8 lg:p-12">
                    <div className="max-w-4xl mx-auto">
                        {/* Subject */}
                        <div className="flex items-start justify-between mb-8">
                            <h1 className="text-2xl md:text-3xl font-normal text-gray-900 dark:text-gray-100 leading-tight">
                                {email.subject}
                            </h1>
                            <div className="flex items-center space-x-2 mt-2">
                                <span className={clsx(
                                    "px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider",
                                    email.category === 'CRITICAL' && "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
                                    email.category === 'OPPORTUNITY' && "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
                                    email.category === 'INFO' && "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
                                    email.category === 'JUNK' && "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400"
                                )}>
                                    {email.category}
                                </span>
                                <Star className="w-5 h-5 text-gray-300 cursor-pointer" />
                            </div>
                        </div>

                        {/* Sender Header */}
                        <div className="flex items-center justify-between mb-8">
                            <div className="flex items-center space-x-4">
                                <div className="w-10 h-10 rounded-full bg-indigo-100 dark:bg-indigo-900/40 flex items-center justify-center text-indigo-700 dark:text-indigo-300 font-bold uppercase">
                                    {email.sender.charAt(0)}
                                </div>
                                <div>
                                    <div className="flex items-center space-x-2">
                                        <span className="font-bold text-gray-900 dark:text-gray-100">{email.sender.split('<')[0].trim() || email.sender}</span>
                                        <span className="text-xs text-gray-500 font-normal">
                                            {email.sender.includes('<') ? email.sender.match(/<([^>]+)>/)[0] : `<${email.sender}>`}
                                        </span>
                                    </div>
                                    <div className="text-xs text-gray-500 flex items-center">
                                        to me 
                                        <button className="ml-1 p-0.5 hover:bg-gray-100 dark:hover:bg-gray-800 rounded transition-colors"><MoreVertical className="w-3 h-3 rotate-90" /></button>
                                    </div>
                                </div>
                            </div>
                            <div className="flex items-center space-x-4 text-xs text-gray-500">
                                <span>{format(new Date(email.received_at), 'PPP (p)')}</span>
                                <div className="flex space-x-1">
                                    <button className="p-1 hover:bg-gray-100 dark:hover:bg-gray-800 rounded transition-colors"><CornerUpLeft className="w-4 h-4" /></button>
                                    <button className="p-1 hover:bg-gray-100 dark:hover:bg-gray-800 rounded transition-colors"><MoreVertical className="w-4 h-4" /></button>
                                </div>
                            </div>
                        </div>

                        {/* Email Body */}
                        <div className="email-body-content dark:text-gray-300 leading-relaxed min-h-[300px]">
                            {email.body ? (
                                <div dangerouslySetInnerHTML={{ __html: email.body }} />
                            ) : (
                                <p className="text-gray-400 italic">No content available.</p>
                            )}
                        </div>

                        {/* Attachments */}
                        {email.attachments && email.attachments.length > 0 && (
                            <div className="mt-12 pt-8 border-t border-gray-100 dark:border-gray-800">
                                <h4 className="text-sm font-bold text-gray-900 dark:text-gray-100 mb-4 flex items-center">
                                    <Paperclip className="w-4 h-4 mr-2" />
                                    {email.attachments.length} Attachments
                                </h4>
                                <div className="flex flex-wrap gap-3">
                                    {email.attachments.map(att => (
                                        <div key={att.id} className="flex items-center p-2 pr-4 border border-gray-200 dark:border-gray-800 rounded-lg bg-gray-50 dark:bg-gray-900/50 hover:bg-gray-100 transition-colors cursor-pointer group">
                                            <div className="w-8 h-8 bg-indigo-50 dark:bg-indigo-900/30 rounded flex items-center justify-center mr-3 text-indigo-600">
                                                <Paperclip className="w-4 h-4" />
                                            </div>
                                            <div className="max-w-[150px]">
                                                <p className="text-xs font-bold text-gray-800 dark:text-gray-200 truncate">{att.filename}</p>
                                                <p className="text-[10px] text-gray-500">{(att.size / 1024).toFixed(1)} KB</p>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Bottom Reply/Forward Actions */}
                        <div className="mt-12 flex space-x-3">
                            <button className="flex items-center px-6 py-2 border border-gray-300 dark:border-gray-700 rounded-full text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 font-medium transition-colors">
                                <CornerUpLeft className="w-4 h-4 mr-2" />
                                Reply
                            </button>
                            <button className="flex items-center px-6 py-2 border border-gray-300 dark:border-gray-700 rounded-full text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 font-medium transition-colors">
                                <CornerUpRight className="w-4 h-4 mr-2" />
                                Forward
                            </button>
                        </div>
                    </div>
                </div>

                {/* Right Pipeline/Task Sidebar (AI Insight Overlay) */}
                <div className="hidden xl:block w-80 bg-gray-50 dark:bg-gray-900/50 border-l border-gray-100 dark:border-gray-800 p-6 overflow-y-auto">
                    <div className="space-y-6">
                        {/* Summary */}
                        {email.summary && (
                            <section className="bg-white dark:bg-gray-950 p-5 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-800">
                                <div className="flex items-center mb-4 space-x-2">
                                    <div className="p-1.5 bg-indigo-50 dark:bg-indigo-900/30 rounded-lg">
                                        <Sparkles className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                                    </div>
                                    <h3 className="text-xs font-black uppercase tracking-widest text-gray-500">AI Summary</h3>
                                </div>
                                <p className="text-sm font-medium text-gray-700 dark:text-gray-300 leading-relaxed italic">
                                    "{email.summary}"
                                </p>
                            </section>
                        )}

                        {/* Tasks */}
                        {email.tasks && email.tasks.length > 0 && (
                            <section className="bg-white dark:bg-gray-950 p-5 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-800">
                                <div className="flex items-center mb-4 space-x-2">
                                    <div className="p-1.5 bg-green-50 dark:bg-green-900/30 rounded-lg">
                                        <CheckSquare className="w-4 h-4 text-green-600 dark:text-green-400" />
                                    </div>
                                    <h3 className="text-xs font-black uppercase tracking-widest text-gray-500">Detected Actions</h3>
                                </div>
                                <div className="space-y-3">
                                    {email.tasks.map(task => (
                                        <div key={task.id} className="group relative flex items-start p-3 bg-gray-50/50 dark:bg-gray-900/50 rounded-xl border border-transparent hover:border-green-200 transition-all">
                                            <button 
                                              onClick={() => handleToggleComplete(task.id, task.is_completed)}
                                              className={clsx(
                                                "mt-0.5 mr-3 flex-shrink-0 w-4 h-4 rounded border-2 transition-colors",
                                                task.is_completed ? "bg-green-500 border-green-500 text-white flex items-center justify-center" : "border-gray-300 dark:border-gray-700"
                                              )}
                                            >
                                                {task.is_completed && <CheckSquare className="w-3 h-3" />}
                                            </button>
                                            <div className="min-w-0">
                                                <p className={clsx(
                                                    "text-xs font-bold transition-all",
                                                    task.is_completed ? "text-gray-400 line-through" : "text-gray-900 dark:text-gray-100"
                                                )}>
                                                    {task.action_text}
                                                </p>
                                                {task.deadline && (
                                                    <div className="flex items-center mt-2 text-[10px] font-black text-indigo-600 dark:text-indigo-400 uppercase tracking-tighter">
                                                        <Clock className="w-3 h-3 mr-1" />
                                                        {format(new Date(task.deadline), 'MMM d, h:mm a')}
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </section>
                        )}
                        
                        {!email.tasks?.length && !email.summary && (
                             <div className="text-center py-12 opacity-50">
                                 <Mail className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                                 <p className="text-xs font-bold text-gray-500">No automated insights for this email.</p>
                             </div>
                        )}
                    </div>
                </div>
            </div>
        </motion.div>
    );
};

export default EmailDetail;