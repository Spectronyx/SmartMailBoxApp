import React, { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { emailService } from '../services/api';
import {
  Search,
  Filter,
  Sparkles,
  RefreshCw,
  AlertCircle,
  Clock,
  Trash2,
  Info
} from 'lucide-react';
import { clsx } from 'clsx';
import { format } from 'date-fns';

const Inbox = () => {
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [searchParams, setSearchParams] = useSearchParams();

  const currentCategory = searchParams.get('category') || 'ALL';

  const fetchEmails = async (showLoading = true) => {
    try {
      if (showLoading) setLoading(true);
      const params = {};
      if (currentCategory !== 'ALL') {
        params.category = currentCategory;
      }
      const response = await emailService.getAll(params);
      setEmails(response.data.results);
    } catch (error) {
      console.error("Failed to fetch emails", error);
    } finally {
      if (showLoading) setLoading(false);
    }
  };

  useEffect(() => {
    fetchEmails();

    const interval = setInterval(() => {
      fetchEmails(false);
    }, 30000);

    return () => clearInterval(interval);
  }, [currentCategory]);

  const handleRunAI = async () => {
    try {
      setProcessing(true);
      // Run classification, summarization, and extraction
      await emailService.classifyAll();
      await emailService.summarizeAll();
      await emailService.extractTasks();

      // Refresh list
      await fetchEmails();
      alert("AI Processing Complete!");
    } catch (error) {
      console.error("AI processing failed", error);
      alert("AI processing failed. Check console.");
    } finally {
      setProcessing(false);
    }
  };

  const categories = [
    { id: 'ALL', label: 'All Mail' },
    { id: 'CRITICAL', label: 'Critical', icon: AlertCircle, color: 'text-red-600' },
    { id: 'OPPORTUNITY', label: 'Opportunities', icon: Sparkles, color: 'text-green-600' },
    { id: 'INFO', label: 'Info & Updates', icon: Info, color: 'text-blue-600' },
    { id: 'JUNK', label: 'Junk', icon: Trash2, color: 'text-gray-500' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <h1 className="text-2xl font-bold text-gray-900">Unified Inbox</h1>
        <div className="flex space-x-3">
          <button
            onClick={fetchEmails}
            className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg"
            title="Refresh"
          >
            <RefreshCw className="w-5 h-5" />
          </button>
          <button
            onClick={handleRunAI}
            disabled={processing}
            className={clsx(
              "flex items-center px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:from-indigo-700 hover:to-purple-700 shadow-sm transition-all",
              processing && "opacity-75 cursor-wait"
            )}
          >
            <Sparkles className={clsx("w-4 h-4 mr-2", processing && "animate-spin")} />
            {processing ? 'AI Processing...' : 'Run AI Agent'}
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex overflow-x-auto pb-2 space-x-2 no-scrollbar">
        {categories.map(cat => (
          <button
            key={cat.id}
            onClick={() => setSearchParams({ category: cat.id === 'ALL' ? [] : cat.id })}
            className={clsx(
              "flex items-center px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-colors",
              currentCategory === cat.id
                ? "bg-gray-900 text-white"
                : "bg-white text-gray-600 border border-gray-200 hover:bg-gray-50"
            )}
          >
            {cat.icon && <cat.icon className={clsx("w-4 h-4 mr-2", cat.color)} />}
            {cat.label}
          </button>
        ))}
      </div>

      {/* Email List */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        {loading ? (
          <div className="p-12 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto"></div>
          </div>
        ) : emails.length === 0 ? (
          <div className="p-12 text-center text-gray-500">
            No emails found in this category.
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {emails.map((email) => (
              <Link
                to={`/emails/${email.id}`}
                key={email.id}
                className="block hover:bg-gray-50 transition-colors"
              >
                <div className="p-4 sm:px-6">
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center space-x-3">
                      <span className={clsx(
                        "px-2 py-0.5 text-xs font-bold rounded uppercase tracking-wider",
                        email.category === 'CRITICAL' && "bg-red-100 text-red-800",
                        email.category === 'OPPORTUNITY' && "bg-green-100 text-green-800",
                        email.category === 'INFO' && "bg-blue-100 text-blue-800",
                        email.category === 'JUNK' && "bg-gray-100 text-gray-800",
                        !email.category && "bg-gray-100 text-gray-600"
                      )}>
                        {email.category || 'Unclassified'}
                      </span>
                      <span className="text-sm text-gray-500 flex items-center">
                        <Clock className="w-3 h-3 mr-1" />
                        {tryFormatDate(email.received_at)}
                      </span>
                    </div>
                  </div>
                  <div className="flex justify-between">
                    <div className="flex-1 min-w-0">
                      <h4 className="text-sm font-semibold text-gray-900 truncate">
                        {email.sender}
                      </h4>
                      <p className="text-sm font-medium text-gray-900 mt-0.5 truncate">
                        {email.subject}
                      </p>
                      <p className="text-sm text-gray-400 mt-1 line-clamp-2">
                        {email.summary || email.snippet}
                      </p>
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

const tryFormatDate = (dateString) => {
  try {
    return format(new Date(dateString), 'MMM d, h:mm a');
  } catch (e) {
    return dateString;
  }
};

export default Inbox;