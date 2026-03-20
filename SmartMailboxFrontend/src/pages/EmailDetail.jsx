import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { emailService } from '../services/api';
import { ArrowLeft, Sparkles, CheckSquare, Clock, User, Paperclip } from 'lucide-react';
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
            // Optimistic UI update
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
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        </div>
    );
    if (!email) return null;

    return (
        <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-4xl mx-auto space-y-6 pb-12"
        >
            <button
                onClick={() => navigate(-1)}
                className="flex items-center text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors font-medium text-sm group"
            >
                <ArrowLeft className="w-4 h-4 mr-1 group-hover:-translate-x-1 transition-transform" />
                Back to Inbox
            </button>

            {/* Header Card */}
            <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-800 p-6 md:p-8 transition-all duration-300">
                <div className="flex flex-col md:flex-row justify-between items-start gap-4">
                    <h1 className="text-2xl md:text-3xl font-black text-gray-900 dark:text-gray-100 tracking-tight leading-tight">
                        {email.subject}
                    </h1>
                    <span className={clsx(
                        "px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-[0.1em] shadow-sm",
                        email.category === 'CRITICAL' && "bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300",
                        email.category === 'OPPORTUNITY' && "bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300",
                        email.category === 'INFO' && "bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300",
                        email.category === 'JUNK' && "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300"
                    )}>
                        {email.category || 'Unclassified'}
                    </span>
                </div>

                <div className="mt-6 flex flex-wrap items-center gap-6 text-sm">
                    <div className="flex items-center text-gray-600 dark:text-gray-400 font-medium">
                        <div className="w-8 h-8 rounded-full bg-indigo-50 dark:bg-indigo-900/30 flex items-center justify-center mr-3">
                            <User className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                        </div>
                        <span className="truncate max-w-[200px]">{email.sender}</span>
                    </div>
                    <div className="flex items-center text-gray-400 dark:text-gray-500 text-xs font-bold uppercase tracking-widest">
                        <Clock className="w-4 h-4 mr-2" />
                        {format(new Date(email.received_at), 'PPP p')}
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 space-y-6">
                    {/* AI Summary Section */}
                    {email.summary && (
                        <div className="bg-gradient-to-br from-indigo-600 to-purple-700 dark:from-indigo-600 dark:to-purple-900 rounded-2xl p-6 shadow-lg shadow-indigo-200 dark:shadow-none">
                            <div className="flex items-center mb-3">
                                <Sparkles className="w-5 h-5 text-indigo-100 mr-2" />
                                <h2 className="text-lg font-black text-white uppercase tracking-wider">AI Summary</h2>
                            </div>
                            <p className="text-indigo-50 leading-relaxed font-medium">
                                {email.summary}
                            </p>
                        </div>
                    )}

                    {/* Email Body */}
                    <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-800 p-6 md:p-8 transition-all duration-300">
                        <h3 className="text-[10px] font-black text-gray-400 dark:text-gray-600 uppercase tracking-[0.2em] mb-6">Original Message</h3>
                        {email.body ? (
                            <div 
                                className="email-body-content dark:text-gray-300"
                                dangerouslySetInnerHTML={{ __html: email.body }}
                            />
                        ) : (
                            <div className="text-gray-400 italic py-16 text-center bg-gray-50 dark:bg-gray-800/50 rounded-xl border-2 border-dashed border-gray-100 dark:border-gray-800">
                                <p>This message has no readable content.</p>
                            </div>
                        )}
                    </div>
                </div>

                <div className="space-y-6">
                    {/* Extracted Tasks Section */}
                    {email.tasks && email.tasks.length > 0 && (
                        <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-sm border border-indigo-100 dark:border-indigo-900/30 p-6 transition-all duration-300 h-fit">
                            <div className="flex items-center mb-6">
                                <CheckSquare className="w-5 h-5 text-indigo-600 dark:text-indigo-400 mr-2" />
                                <h3 className="text-xs font-black text-gray-900 dark:text-gray-100 uppercase tracking-widest">Tasks</h3>
                            </div>
                            <div className="space-y-4">
                                <AnimatePresence mode="popLayout">
                                    {email.tasks.map(task => (
                                        <motion.div 
                                            layout
                                            initial={{ opacity: 0, scale: 0.9 }}
                                            animate={{ opacity: 1, scale: 1 }}
                                            key={task.id} 
                                            className={clsx(
                                                "p-4 rounded-xl border transition-all",
                                                task.is_completed 
                                                    ? "bg-gray-50 dark:bg-gray-800/30 border-gray-100 dark:border-gray-800 opacity-60" 
                                                    : "bg-indigo-50/50 dark:bg-indigo-900/10 border-indigo-100/50 dark:border-indigo-800/30 shadow-sm"
                                            )}
                                        >
                                            <div className="flex items-start space-x-3">
                                                <button
                                                    onClick={() => handleToggleComplete(task.id, task.is_completed)}
                                                    className="mt-1 flex-shrink-0 focus:outline-none transition-transform active:scale-90"
                                                >
                                                    {task.is_completed ? (
                                                        <CheckSquare className="w-5 h-5 text-green-500 dark:text-green-400 fill-green-50 dark:fill-green-900/20" />
                                                    ) : (
                                                        <div className="w-5 h-5 border-2 border-indigo-300 dark:border-indigo-700 rounded transition-colors bg-white dark:bg-gray-800" />
                                                    )}
                                                </button>
                                                <div className="min-w-0">
                                                    <p className={clsx(
                                                        "text-sm font-bold leading-snug transition-all duration-300",
                                                        task.is_completed ? "text-gray-400 dark:text-gray-600 line-through" : "text-gray-900 dark:text-gray-200"
                                                    )}>
                                                        {task.action_text}
                                                    </p>
                                                    {task.deadline && (
                                                        <p className="text-[10px] text-indigo-600 dark:text-indigo-400 font-black mt-2 flex items-center uppercase tracking-wider">
                                                            <Clock className="w-3 h-3 mr-1" />
                                                            {format(new Date(task.deadline), 'MMM d, h:mm a')}
                                                        </p>
                                                    )}
                                                </div>
                                            </div>
                                        </motion.div>
                                    ))}
                                </AnimatePresence>
                            </div>
                        </div>
                    )}

                    {/* Attachments Section */}
                    {email.attachments && email.attachments.length > 0 && (
                        <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-800 p-6 transition-all duration-300">
                            <div className="flex items-center mb-6">
                                <Paperclip className="w-5 h-5 text-gray-400 dark:text-gray-500 mr-2" />
                                <h2 className="text-xs font-black text-gray-900 dark:text-gray-100 uppercase tracking-widest">Files ({email.attachments.length})</h2>
                            </div>
                            <div className="space-y-3">
                                {email.attachments.map(att => (
                                    <div key={att.id} className="group flex items-center p-3 border border-gray-100 dark:border-gray-800 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-800 transition-all cursor-pointer">
                                        <div className="p-2 bg-gray-50 dark:bg-gray-800 group-hover:bg-white dark:group-hover:bg-gray-700 rounded-lg mr-3 transition-colors">
                                            <Paperclip className="w-4 h-4 text-gray-400 dark:text-gray-500" />
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <p className="text-xs font-bold text-gray-700 dark:text-gray-300 truncate">{att.filename}</p>
                                            <p className="text-[10px] text-gray-400 dark:text-gray-500 font-medium uppercase tracking-tighter">
                                                {(att.size / 1024).toFixed(1)} KB • {att.content_type.split('/')[1] || 'FILE'}
                                            </p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </motion.div>
    );
};

export default EmailDetail;