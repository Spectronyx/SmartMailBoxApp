import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { emailService } from '../services/api';
import { ArrowLeft, Sparkles, CheckSquare, Calendar, User, Clock } from 'lucide-react';
import { format } from 'date-fns';
import { clsx } from 'clsx';

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

    if (loading) return <div>Loading...</div>;
    if (!email) return null;

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            <button
                onClick={() => navigate(-1)}
                className="flex items-center text-gray-500 hover:text-gray-900 transition-colors"
            >
                <ArrowLeft className="w-4 h-4 mr-1" />
                Back to Inbox
            </button>

            {/* Header */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                <div className="flex justify-between items-start">
                    <h1 className="text-2xl font-bold text-gray-900">{email.subject}</h1>
                    <span className={clsx(
                        "px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider",
                        email.category === 'CRITICAL' && "bg-red-100 text-red-800",
                        email.category === 'OPPORTUNITY' && "bg-green-100 text-green-800",
                        email.category === 'INFO' && "bg-blue-100 text-blue-800",
                        email.category === 'JUNK' && "bg-gray-100 text-gray-800"
                    )}>
                        {email.category}
                    </span>
                </div>

                <div className="mt-4 flex items-center space-x-6 text-sm text-gray-500">
                    <div className="flex items-center">
                        <User className="w-4 h-4 mr-2" />
                        {email.sender}
                    </div>
                    <div className="flex items-center">
                        <Clock className="w-4 h-4 mr-2" />
                        {format(new Date(email.received_at), 'PPP p')}
                    </div>
                </div>
            </div>

            {/* AI Summary Section */}
            {email.summary && (
                <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl border border-indigo-100 p-6">
                    <div className="flex items-center mb-3">
                        <Sparkles className="w-5 h-5 text-indigo-600 mr-2" />
                        <h2 className="text-lg font-semibold text-indigo-900">AI Summary</h2>
                    </div>
                    <p className="text-indigo-800 leading-relaxed">
                        {email.summary}
                    </p>
                </div>
            )}

            {/* Attachments Section */}
            {email.attachments && email.attachments.length > 0 && (
                <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                    <h2 className="text-lg font-semibold text-gray-900 mb-4">Attachments ({email.attachments.length})</h2>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        {email.attachments.map(att => (
                            <div key={att.id} className="flex items-center p-3 border border-gray-100 rounded-lg hover:bg-gray-50 transition-colors">
                                <div className="p-2 bg-gray-100 rounded mr-3">
                                    <CheckSquare className="w-4 h-4 text-gray-500" />
                                </div>
                                <div className="flex-1 min-w-0">
                                    <p className="text-sm font-medium text-gray-900 truncate">{att.filename}</p>
                                    <p className="text-xs text-gray-500">{(att.size / 1024).toFixed(1)} KB • {att.content_type}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Extracted Tasks Section */}
            {email.tasks && email.tasks.length > 0 && (
                <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl shadow-sm border border-indigo-100 p-6 mb-8">
                    <div className="flex items-center mb-4">
                        <CheckSquare className="w-5 h-5 text-indigo-600 mr-2" />
                        <h3 className="text-sm font-bold text-indigo-900 uppercase tracking-wider">Extracted Action Items</h3>
                    </div>
                    <div className="space-y-4">
                        {email.tasks.map(task => (
                            <div key={task.id} className="bg-white/80 p-4 rounded-lg border border-indigo-100/50 flex justify-between items-start">
                                <div>
                                    <p className="font-medium text-gray-900">{task.action_text}</p>
                                    {task.deadline && (
                                        <p className="text-xs text-indigo-600 font-semibold mt-1">
                                            Due: {new Date(task.deadline).toLocaleString()}
                                        </p>
                                    )}
                                </div>
                                {task.reminder_sent && (
                                    <span className="px-2 py-1 bg-green-100 text-green-700 text-[10px] font-bold rounded-full">
                                        REMINDER SENT
                                    </span>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Email Body */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8">
                <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4">Original Message</h3>
                {email.body ? (
                    <div 
                        className="email-body-content font-sans"
                        dangerouslySetInnerHTML={{ __html: email.body }}
                    />
                ) : (
                    <div className="text-gray-400 italic py-10 text-center bg-gray-50 rounded-lg">
                        <p>No message content available to display.</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default EmailDetail;