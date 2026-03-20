import React, { useEffect, useState } from 'react';
import { clsx } from 'clsx';
import { format } from 'date-fns';
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
  Info, 
  X, 
  Paperclip, 
  Calendar,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { mailboxService } from '../services/api';

const Inbox = () => {
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [lastSynced, setLastSynced] = useState(null);
  const [searchParams, setSearchParams] = useSearchParams();
  
  // UI State
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [searchQuery, setSearchQuery] = useState(searchParams.get('search') || '');

  // Filter State from Params
  const currentCategory = searchParams.get('category') || 'ALL';
  const hasAttachments = searchParams.get('has_attachments') === 'true';
  const dateAfter = searchParams.get('received_at_after') || '';
  const dateBefore = searchParams.get('received_at_before') || '';

  const fetchEmails = async (showLoading = true) => {
    try {
      if (showLoading) setLoading(true);
      
      const params = Object.fromEntries(searchParams.entries());
      if (params.category === 'ALL') delete params.category;
      
      const [emailRes, mailboxRes] = await Promise.all([
        emailService.getAll(params),
        mailboxService.getAll()
      ]);
      
      setEmails(emailRes.data.results);
      
      const syncTimes = (mailboxRes.data.results || [])
        .map(mb => mb.last_synced_at)
        .filter(Boolean)
        .map(ts => new Date(ts));
      
      if (syncTimes.length > 0) {
        setLastSynced(new Date(Math.max(...syncTimes)));
      }
    } catch (error) {
      console.error("Failed to fetch emails", error);
    } finally {
      if (showLoading) setLoading(false);
    }
  };

  useEffect(() => {
    fetchEmails();
    const interval = setInterval(() => fetchEmails(false), 30000);
    return () => clearInterval(interval);
  }, [searchParams]);

  const handleSearch = (e) => {
    e.preventDefault();
    const newParams = new URLSearchParams(searchParams);
    if (searchQuery) {
        newParams.set('search', searchQuery);
    } else {
        newParams.delete('search');
    }
    setSearchParams(newParams);
  };

  const updateParam = (key, value) => {
    const newParams = new URLSearchParams(searchParams);
    if (value) {
        newParams.set(key, value);
    } else {
        newParams.delete(key);
    }
    setSearchParams(newParams);
  };

  const clearFilters = () => {
    setSearchParams({});
    setSearchQuery('');
  };

  const handleRunAI = async () => {
    try {
      setProcessing(true);
      await Promise.all([
        emailService.classifyAll(),
        emailService.summarizeAll(),
        emailService.extractTasks()
      ]);
      await fetchEmails();
    } catch (error) {
      console.error("AI processing failed", error);
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

  const activeFilterCount = Array.from(searchParams.keys()).filter(k => k !== 'category').length;

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h1 className="text-2xl font-black text-gray-900 dark:text-gray-100 tracking-tight">Unified Inbox</h1>
          {lastSynced && (
            <p className="text-[10px] text-gray-400 dark:text-gray-500 mt-1 flex items-center uppercase font-black tracking-widest">
              <Clock className="w-3 h-3 mr-1" />
              Fetched {format(lastSynced, 'h:mm:ss a')}
            </p>
          )}
        </div>
        
        <div className="flex items-center gap-3">
          <form onSubmit={handleSearch} className="relative flex-1 md:w-64">
            <input
              type="text"
              placeholder="Search subject, body..."
              className="w-full pl-10 pr-4 py-2.5 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none text-sm transition-all"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <Search className="absolute left-3.5 top-3 w-4 h-4 text-gray-400" />
            {searchQuery && (
              <button 
                type="button"
                onClick={() => { setSearchQuery(''); updateParam('search', ''); }}
                className="absolute right-3 top-3 text-gray-300 hover:text-gray-600"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </form>

          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className={clsx(
              "p-2.5 rounded-xl border transition-all relative",
              showAdvanced || activeFilterCount > 0
                ? "bg-indigo-50 dark:bg-indigo-900/40 border-indigo-200 dark:border-indigo-800 text-indigo-600 dark:text-indigo-400"
                : "bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-800 text-gray-500 hover:bg-gray-50 dark:hover:bg-gray-800"
            )}
          >
            <Filter className="w-5 h-5" />
            {activeFilterCount > 0 && (
              <span className="absolute -top-1 -right-1 w-4 h-4 bg-indigo-600 text-white text-[10px] rounded-full flex items-center justify-center font-bold">
                {activeFilterCount}
              </span>
            )}
          </button>

          <button
            onClick={handleRunAI}
            disabled={processing}
            className="flex items-center px-5 py-2.5 bg-gray-900 dark:bg-white text-white dark:text-gray-900 rounded-xl font-bold text-sm shadow-lg hover:opacity-90 transition-all active:scale-95 disabled:opacity-50"
          >
            <Sparkles className={clsx("w-4 h-4 mr-2", processing && "animate-spin")} />
            {processing ? 'AI...' : 'Run Agent'}
          </button>
        </div>
      </div>

      {/* Advanced Filters Panel */}
      <AnimatePresence>
        {showAdvanced && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <div className="bg-white dark:bg-gray-900 p-6 rounded-2xl border border-gray-100 dark:border-gray-800 shadow-sm grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                    <label className="block text-[10px] font-black uppercase tracking-widest text-gray-400 mb-2">Date Range</label>
                    <div className="flex items-center gap-2">
                        <input 
                            type="date" 
                            className="bg-gray-50 dark:bg-gray-800 border-none rounded-lg text-xs p-2 outline-none focus:ring-1 focus:ring-indigo-500 w-full"
                            value={dateAfter}
                            onChange={(e) => updateParam('received_at_after', e.target.value)}
                        />
                        <span className="text-gray-300">to</span>
                        <input 
                            type="date" 
                            className="bg-gray-50 dark:bg-gray-800 border-none rounded-lg text-xs p-2 outline-none focus:ring-1 focus:ring-indigo-500 w-full"
                            value={dateBefore}
                            onChange={(e) => updateParam('received_at_before', e.target.value)}
                        />
                    </div>
                </div>

                <div>
                    <label className="block text-[10px] font-black uppercase tracking-widest text-gray-400 mb-2">Attachments</label>
                    <button
                        onClick={() => updateParam('has_attachments', hasAttachments ? '' : 'true')}
                        className={clsx(
                            "flex items-center w-full px-4 py-2 rounded-lg border text-sm font-bold transition-all",
                            hasAttachments 
                                ? "bg-indigo-50 dark:bg-indigo-900/20 border-indigo-200 dark:border-indigo-800 text-indigo-600 dark:text-indigo-400" 
                                : "bg-gray-50 dark:bg-gray-800 border-transparent text-gray-500"
                        )}
                    >
                        <Paperclip className="w-4 h-4 mr-2" />
                        Has Attachments
                    </button>
                </div>

                <div className="flex items-end">
                    <button
                        onClick={clearFilters}
                        className="w-full py-2 text-xs font-bold text-gray-400 hover:text-red-500 transition-colors uppercase tracking-widest"
                    >
                        Clear All Filters
                    </button>
                </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="flex overflow-x-auto pb-2 space-x-3 no-scrollbar">
        {categories.map(cat => (
          <button
            key={cat.id}
            onClick={() => updateParam('category', cat.id === 'ALL' ? '' : cat.id)}
            className={clsx(
              "flex items-center px-4 py-2 rounded-full text-xs font-bold uppercase tracking-widest whitespace-nowrap transition-all border",
              currentCategory === cat.id
                ? "bg-indigo-600 border-indigo-600 text-white dark:bg-indigo-500 dark:border-indigo-500 shadow-md"
                : "bg-white dark:bg-gray-900 text-gray-600 dark:text-gray-400 border-gray-200 dark:border-gray-800 hover:border-indigo-300"
            )}
          >
            {cat.icon && <cat.icon className={clsx("w-3.5 h-3.5 mr-2", cat.color)} />}
            {cat.label}
          </button>
        ))}
      </div>

      {/* Email List */}
      <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-800 overflow-hidden transition-all duration-300">
        {loading ? (
          <div className="p-32 text-center">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600 mx-auto"></div>
            <p className="mt-4 text-sm text-gray-400 dark:text-gray-500 font-medium">Scanning your mailbox...</p>
          </div>
        ) : emails.length === 0 ? (
          <div className="p-32 text-center">
            <div className="w-16 h-16 bg-gray-50 dark:bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-4">
                <Search className="w-8 h-8 text-gray-300" />
            </div>
            <h3 className="text-gray-900 dark:text-gray-100 font-bold">No matches found</h3>
            <p className="mt-1 text-sm text-gray-400 dark:text-gray-500">Try adjusting your filters or search query.</p>
            <button 
                onClick={clearFilters}
                className="mt-6 text-indigo-600 dark:text-indigo-400 text-xs font-black uppercase tracking-widest hover:underline"
            >
                Clear all filters
            </button>
          </div>
        ) : (
          <div className="divide-y divide-gray-50 dark:divide-gray-800/50">
            <AnimatePresence mode="popLayout">
              {emails.map((email) => (
                <motion.div
                  layout
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  key={email.id}
                >
                  <Link
                    to={`/emails/${email.id}`}
                    className="block hover:bg-gray-50 dark:hover:bg-gray-800/20 transition-all group"
                  >
                    <div className="p-5 sm:px-8">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center space-x-3">
                          <span className={clsx(
                            "px-2 py-0.5 text-[9px] font-black rounded uppercase tracking-widest shadow-sm",
                            email.category === 'CRITICAL' && "bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300",
                            email.category === 'OPPORTUNITY' && "bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300",
                            email.category === 'INFO' && "bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300",
                            email.category === 'JUNK' && "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300",
                            !email.category && "bg-gray-50 text-gray-400 dark:bg-gray-800 dark:text-gray-500"
                          )}>
                            {email.category || 'Categorizing...'}
                          </span>
                          {email.has_attachments && (
                            <Paperclip className="w-3.5 h-3.5 text-gray-400 dark:text-gray-600" />
                          )}
                        </div>
                        <span className="text-[10px] text-gray-400 dark:text-gray-600 flex items-center font-bold uppercase tracking-widest">
                          {tryFormatDate(email.received_at)}
                        </span>
                      </div>
                      <div className="flex justify-between gap-6">
                        <div className="flex-1 min-w-0">
                          <h4 className="text-sm font-bold text-gray-900 dark:text-gray-200 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors truncate">
                            {email.sender}
                          </h4>
                          <p className="text-sm font-black text-gray-800 dark:text-gray-100 mt-1 truncate leading-tight">
                            {email.subject}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 line-clamp-2 leading-relaxed">
                            {email.summary || email.snippet}
                          </p>
                        </div>
                      </div>
                    </div>
                  </Link>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
      </div>
    </div>
  );
};

const tryFormatDate = (dateString) => {
  try {
    const date = new Date(dateString);
    const now = new Date();
    if (date.toDateString() === now.toDateString()) {
        return format(date, 'h:mm a');
    }
    return format(date, 'MMM d');
  } catch (e) {
    return dateString;
  }
};

export default Inbox;