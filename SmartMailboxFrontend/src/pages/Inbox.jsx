import React, { useEffect, useState, useRef } from 'react';
import { clsx } from 'clsx';
import { format, isToday, isThisYear } from 'date-fns';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { emailService, mailboxService } from '../services/api';
import { 
  Search, 
  Filter, 
  Sparkles, 
  RefreshCw, 
  AlertCircle, 
  Clock, 
  Trash2, 
  Info, 
  Paperclip, 
  Star,
  Archive,
  CheckSquare,
  MoreVertical,
  Check,
  Mail,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const Inbox = () => {
    const navigate = useNavigate();
    const [emails, setEmails] = useState([]);
    const [loading, setLoading] = useState(true);
    const [processing, setProcessing] = useState(false);
    const [lastSynced, setLastSynced] = useState(null);
    const [searchParams, setSearchParams] = useSearchParams();
    const [selectedEmails, setSelectedEmails] = useState(new Set());
    const pollRef = useRef(null);
    
    // Pagination State
    const [totalCount, setTotalCount] = useState(0);
    const [nextPageUrl, setNextPageUrl] = useState(null);
    const [prevPageUrl, setPrevPageUrl] = useState(null);
    const currentPage = parseInt(searchParams.get('page') || '1', 10);
    const pageSize = 20; // matches backend PAGE_SIZE
    const totalPages = Math.max(1, Math.ceil(totalCount / pageSize));

    // UI State
    const [showAdvanced, setShowAdvanced] = useState(false);
    const [searchQuery, setSearchQuery] = useState(searchParams.get('search') || '');

    // Filter State from Params
    const currentCategory = searchParams.get('category') || 'ALL';
    const hasAttachments = searchParams.get('has_attachments') === 'true';
    const dateAfter = searchParams.get('received_at_after') || '';

    const fetchEmails = async (showLoading = true) => {
        try {
            if (showLoading) setLoading(true);
            const params = Object.fromEntries(searchParams.entries());
            if (params.category === 'ALL') delete params.category;
            
            const [emailRes, mailboxRes] = await Promise.all([
                emailService.getAll(params),
                mailboxService.getAll()
            ]);
            
            const data = emailRes.data;
            setEmails(data.results || []);
            setTotalCount(data.count || 0);
            setNextPageUrl(data.next);
            setPrevPageUrl(data.previous);
            
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
        pollRef.current = setInterval(() => fetchEmails(false), 30000);
        return () => clearInterval(pollRef.current);
    }, [searchParams]);

    const handleSearch = (e) => {
        e.preventDefault();
        const newParams = new URLSearchParams(searchParams);
        if (searchQuery) newParams.set('search', searchQuery);
        else newParams.delete('search');
        newParams.delete('page'); // Reset to page 1 on search
        setSearchParams(newParams);
    };

    const updateParam = (key, value) => {
        const newParams = new URLSearchParams(searchParams);
        if (value) newParams.set(key, value);
        else newParams.delete(key);
        newParams.delete('page'); // Reset to page 1 on filter change
        setSearchParams(newParams);
    };

    const goToPage = (page) => {
        const newParams = new URLSearchParams(searchParams);
        if (page <= 1) newParams.delete('page');
        else newParams.set('page', String(page));
        setSearchParams(newParams);
        // Scroll to top of email list
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const toggleSelectAll = () => {
        if (selectedEmails.size === emails.length) {
            setSelectedEmails(new Set());
        } else {
            setSelectedEmails(new Set(emails.map(e => e.id)));
        }
    };

    const toggleSelect = (e, id) => {
        e.stopPropagation();
        const next = new Set(selectedEmails);
        if (next.has(id)) next.delete(id);
        else next.add(id);
        setSelectedEmails(next);
    };

    const handleRunAI = async () => {
        try {
            setProcessing(true);
            await emailService.classifyAll();
            await emailService.summarizeAll();
            await emailService.extractTasks();
            await fetchEmails();
        } catch (error) {
            console.error("AI processing failed", error);
        } finally {
            setProcessing(false);
        }
    };

    const categories = [
        { id: 'ALL', label: 'Primary', icon: Mail },
        { id: 'CRITICAL', label: 'High Priority', icon: AlertCircle, color: 'text-red-500' },
        { id: 'OPPORTUNITY', label: 'Promos', icon: Sparkles, color: 'text-emerald-500' },
        { id: 'INFO', label: 'Updates', icon: Info, color: 'text-blue-500' },
        { id: 'JUNK', label: 'Spam', icon: Trash2, color: 'text-gray-400' },
    ];

    // Calculate which emails we're showing
    const startItem = totalCount === 0 ? 0 : (currentPage - 1) * pageSize + 1;
    const endItem = Math.min(currentPage * pageSize, totalCount);

    return (
        <div className="flex flex-col h-full bg-white dark:bg-gray-950 transition-colors duration-300 -m-4 md:-m-8">
            {/* Header / Search Bar */}
            <div className="sticky top-0 z-20 px-4 md:px-8 py-4 bg-white/80 dark:bg-gray-950/80 backdrop-blur-md border-b border-gray-100 dark:border-gray-800">
                <div className="flex items-center gap-4 max-w-5xl mx-auto">
                    <div className="flex-1 relative group">
                        <form onSubmit={handleSearch}>
                            <input
                                type="text"
                                placeholder="Search mail"
                                className="w-full pl-12 pr-4 py-2.5 bg-gray-100 dark:bg-gray-900/50 border-none rounded-2xl focus:bg-white dark:focus:bg-gray-900 focus:ring-2 focus:ring-indigo-500/20 outline-none text-sm transition-all shadow-sm group-hover:shadow-md"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                            />
                        </form>
                        <Search className="absolute left-4 top-3 w-4.5 h-4.5 text-gray-400 group-hover:text-indigo-500 transition-colors" />
                        <button 
                            onClick={() => setShowAdvanced(!showAdvanced)}
                            className="absolute right-4 top-2.5 p-1 hover:bg-gray-200 dark:hover:bg-gray-800 rounded-md transition-colors"
                        >
                            <Filter className="w-4 h-4 text-gray-500" />
                        </button>
                    </div>
                    
                    <button
                        onClick={handleRunAI}
                        disabled={processing}
                        className={clsx(
                            "hidden sm:flex items-center px-6 py-2.5 rounded-2xl font-black text-xs uppercase tracking-widest transition-all active:scale-95 shadow-lg",
                            processing 
                                ? "bg-gray-100 text-gray-400 cursor-not-allowed" 
                                : "bg-indigo-600 text-white hover:bg-indigo-700 shadow-indigo-200 dark:shadow-none"
                        )}
                    >
                        <Sparkles className={clsx("w-3.5 h-3.5 mr-2", processing && "animate-spin")} />
                        {processing ? 'Processing...' : 'Run Agent'}
                    </button>
                </div>

                <AnimatePresence>
                    {showAdvanced && (
                        <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: "auto", opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            className="max-w-5xl mx-auto mt-4 overflow-hidden"
                        >
                            <div className="p-6 bg-white dark:bg-gray-900 rounded-2xl border border-gray-100 dark:border-gray-800 shadow-xl grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                <div>
                                    <label className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">From Date</label>
                                    <input 
                                        type="date" 
                                        className="w-full mt-1 p-2 bg-gray-50 dark:bg-gray-800 rounded-lg text-xs outline-none border border-transparent focus:border-indigo-300"
                                        value={dateAfter}
                                        onChange={(e) => updateParam('received_at_after', e.target.value)}
                                    />
                                </div>
                                <div>
                                    <label className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">Has Attachment</label>
                                    <button 
                                        onClick={() => updateParam('has_attachments', hasAttachments ? '' : 'true')}
                                        className={clsx(
                                            "w-full mt-1 p-2 rounded-lg text-xs font-bold text-left border flex items-center justify-between",
                                            hasAttachments ? "bg-indigo-50 border-indigo-200 text-indigo-600" : "bg-gray-50 border-transparent text-gray-500"
                                        )}
                                    >
                                        Yes/No
                                        {hasAttachments && <Check className="w-3 h-3" />}
                                    </button>
                                </div>
                                <div className="md:col-span-2 lg:col-span-1 flex items-end">
                                    <button 
                                        onClick={() => { setSearchParams({}); setSearchQuery(''); }}
                                        className="text-[10px] font-black uppercase tracking-widest text-red-500 hover:underline"
                                    >
                                        Clear All Filters
                                    </button>
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>

            {/* Sub-Header: Selection & Tabs */}
            <div className="px-4 md:px-8 bg-white dark:bg-gray-950 border-b border-gray-100 dark:border-gray-800 sticky top-[73px] z-10 transition-colors">
                <div className="flex items-center justify-between py-2 max-w-5xl mx-auto">
                    <div className="flex items-center space-x-2">
                        <button 
                            onClick={toggleSelectAll}
                            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded transition-colors text-gray-400"
                        >
                            {selectedEmails.size === emails.length && emails.length > 0 ? (
                                <CheckSquare className="w-4.5 h-4.5 text-indigo-600" />
                            ) : (
                                <div className="w-4.5 h-4.5 border-2 border-gray-300 rounded" />
                            )}
                        </button>
                        <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded text-gray-500"><RefreshCw className="w-4.5 h-4.5" /></button>
                        <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded text-gray-500"><MoreVertical className="w-4.5 h-4.5" /></button>
                        
                        {/* Page info + nav (inline like Gmail) */}
                        {totalCount > 0 && (
                            <div className="hidden sm:flex items-center ml-4 text-xs text-gray-500 space-x-1">
                                <span className="font-medium">{startItem}–{endItem}</span>
                                <span>of</span>
                                <span className="font-medium">{totalCount}</span>
                                <div className="flex items-center ml-2">
                                    <button
                                        onClick={() => goToPage(1)}
                                        disabled={currentPage <= 1}
                                        className="p-1 hover:bg-gray-100 dark:hover:bg-gray-800 rounded disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                                    >
                                        <ChevronsLeft className="w-4 h-4" />
                                    </button>
                                    <button
                                        onClick={() => goToPage(currentPage - 1)}
                                        disabled={!prevPageUrl}
                                        className="p-1 hover:bg-gray-100 dark:hover:bg-gray-800 rounded disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                                    >
                                        <ChevronLeft className="w-4 h-4" />
                                    </button>
                                    <button
                                        onClick={() => goToPage(currentPage + 1)}
                                        disabled={!nextPageUrl}
                                        className="p-1 hover:bg-gray-100 dark:hover:bg-gray-800 rounded disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                                    >
                                        <ChevronRight className="w-4 h-4" />
                                    </button>
                                    <button
                                        onClick={() => goToPage(totalPages)}
                                        disabled={currentPage >= totalPages}
                                        className="p-1 hover:bg-gray-100 dark:hover:bg-gray-800 rounded disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                                    >
                                        <ChevronsRight className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>

                    <div className="flex items-center space-x-1 overflow-x-auto">
                        {categories.map(cat => (
                            <button
                                key={cat.id}
                                onClick={() => updateParam('category', cat.id === 'ALL' ? '' : cat.id)}
                                className={clsx(
                                    "px-4 py-2.5 rounded-t-lg border-b-2 text-xs font-bold uppercase tracking-wider transition-all whitespace-nowrap",
                                    currentCategory === cat.id
                                        ? "border-indigo-600 text-indigo-600 bg-indigo-50/30 dark:bg-indigo-900/10"
                                        : "border-transparent text-gray-500 hover:bg-gray-50 dark:hover:bg-gray-900"
                                )}
                            >
                                <span className="flex items-center gap-2">
                                    <cat.icon className={clsx("w-3.5 h-3.5", currentCategory === cat.id ? cat.color : "text-gray-400")} />
                                    {cat.label}
                                </span>
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* Email List */}
            <div className="flex-1 overflow-y-auto bg-white dark:bg-transparent">
                <div className="max-w-5xl mx-auto">
                    {loading ? (
                        <div className="py-20 text-center">
                            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-indigo-600 mx-auto"></div>
                            <p className="mt-4 text-[10px] font-black uppercase tracking-widest text-gray-400">Loading your inbox...</p>
                        </div>
                    ) : emails.length === 0 ? (
                        <div className="py-20 text-center">
                            <Info className="w-12 h-12 text-gray-200 mx-auto mb-4" />
                            <p className="text-sm font-bold text-gray-500">No messages matching your search.</p>
                        </div>
                    ) : (
                        <div className="hover:shadow-lg transition-shadow">
                            {emails.map((email) => (
                                <div
                                    key={email.id}
                                    onClick={() => navigate(`/emails/${email.id}`)}
                                    className={clsx(
                                        "group flex items-center px-4 md:px-6 py-2 border-b border-gray-50 dark:border-gray-900 cursor-pointer transition-colors relative",
                                        email.status === 'UNREAD' ? "bg-white dark:bg-gray-900/40" : "bg-gray-50/30 dark:bg-gray-950",
                                        selectedEmails.has(email.id) ? "bg-indigo-50 !border-indigo-100" : "hover:bg-gray-50 dark:hover:bg-gray-900"
                                    )}
                                >
                                    {/* Select & Star */}
                                    <div className="flex items-center space-x-3 mr-4 flex-shrink-0">
                                        <button 
                                            onClick={(e) => toggleSelect(e, email.id)}
                                            className="opacity-0 group-hover:opacity-100 transition-opacity p-1"
                                        >
                                            {selectedEmails.has(email.id) ? (
                                                <CheckSquare className="w-4 h-4 text-indigo-600" />
                                            ) : (
                                                <div className="w-4 h-4 border-2 border-gray-300 rounded" />
                                            )}
                                        </button>
                                        <Star className="w-4.5 h-4.5 text-gray-300 hover:text-yellow-400 transition-colors" />
                                    </div>

                                    {/* Sender */}
                                    <div className={clsx(
                                        "w-24 md:w-56 flex-shrink-0 text-sm truncate mr-4",
                                        email.status === 'UNREAD' ? "font-black text-gray-900 dark:text-gray-100" : "text-gray-600 dark:text-gray-400"
                                    )}>
                                        {email.sender.split('<')[0].trim() || email.sender}
                                    </div>

                                    {/* Subject & Snippet */}
                                    <div className="flex-1 min-w-0 flex items-baseline truncate mr-4">
                                        <span className={clsx(
                                            "text-sm truncate",
                                            email.status === 'UNREAD' ? "font-black text-gray-900 dark:text-white" : "text-gray-800 dark:text-gray-200 font-medium"
                                        )}>
                                            {email.subject}
                                        </span>
                                        <span className="text-gray-400 dark:text-gray-500 text-xs truncate ml-2">
                                            — {email.summary || email.snippet || "No content"}
                                        </span>
                                        {email.has_attachments && (
                                            <Paperclip className="w-3 h-3 text-gray-400 ml-2 flex-shrink-0" />
                                        )}
                                    </div>

                                    {/* Category Badge */}
                                    {email.category && email.category !== 'UNKNOWN' && (
                                        <span className={clsx(
                                            "hidden md:inline-block text-[9px] font-black uppercase tracking-wider px-2 py-0.5 rounded-full mr-3 flex-shrink-0",
                                            email.category === 'CRITICAL' && "bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400",
                                            email.category === 'OPPORTUNITY' && "bg-emerald-100 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400",
                                            email.category === 'INFO' && "bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400",
                                            email.category === 'JUNK' && "bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400",
                                        )}>
                                            {email.category}
                                        </span>
                                    )}

                                    {/* Date */}
                                    <div className={clsx(
                                        "text-[10px] w-14 text-right flex-shrink-0 font-bold uppercase tracking-tighter opacity-70 group-hover:hidden",
                                        email.status === 'UNREAD' ? "text-indigo-600" : "text-gray-400"
                                    )}>
                                        {formatDateDense(email.received_at)}
                                    </div>

                                    {/* Hover Actions */}
                                    <div className="hidden group-hover:flex items-center space-x-2 w-28 justify-end">
                                        <button className="p-1.5 hover:bg-gray-200 dark:hover:bg-gray-800 rounded-full text-gray-500 transition-colors" title="Archive"><Archive className="w-4 h-4" /></button>
                                        <button className="p-1.5 hover:bg-gray-200 dark:hover:bg-gray-800 rounded-full text-red-500 transition-colors" title="Delete"><Trash2 className="w-4 h-4" /></button>
                                        <button className="p-1.5 hover:bg-gray-200 dark:hover:bg-gray-800 rounded-full text-gray-500 transition-colors" title="Mark as Read"><Mail className="w-4 h-4" /></button>
                                        <button className="p-1.5 hover:bg-gray-200 dark:hover:bg-gray-800 rounded-full text-gray-500 transition-colors" title="Snooze"><Clock className="w-4 h-4" /></button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* Bottom Pagination Bar */}
            {totalCount > pageSize && (
                <div className="bg-white dark:bg-gray-950 border-t border-gray-100 dark:border-gray-800 px-4 md:px-8 py-3">
                    <div className="max-w-5xl mx-auto flex items-center justify-between">
                        <p className="text-xs text-gray-500">
                            Showing <span className="font-bold">{startItem}–{endItem}</span> of <span className="font-bold">{totalCount}</span> emails
                        </p>
                        <div className="flex items-center space-x-1">
                            <button
                                onClick={() => goToPage(1)}
                                disabled={currentPage <= 1}
                                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg disabled:opacity-30 disabled:cursor-not-allowed transition-colors text-gray-600 dark:text-gray-400"
                                title="First page"
                            >
                                <ChevronsLeft className="w-4 h-4" />
                            </button>
                            <button
                                onClick={() => goToPage(currentPage - 1)}
                                disabled={!prevPageUrl}
                                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg disabled:opacity-30 disabled:cursor-not-allowed transition-colors text-gray-600 dark:text-gray-400"
                                title="Previous page"
                            >
                                <ChevronLeft className="w-4 h-4" />
                            </button>

                            {/* Page numbers */}
                            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                                let pageNum;
                                if (totalPages <= 5) {
                                    pageNum = i + 1;
                                } else if (currentPage <= 3) {
                                    pageNum = i + 1;
                                } else if (currentPage >= totalPages - 2) {
                                    pageNum = totalPages - 4 + i;
                                } else {
                                    pageNum = currentPage - 2 + i;
                                }
                                return (
                                    <button
                                        key={pageNum}
                                        onClick={() => goToPage(pageNum)}
                                        className={clsx(
                                            "w-8 h-8 rounded-lg text-xs font-bold transition-all",
                                            currentPage === pageNum
                                                ? "bg-indigo-600 text-white shadow-md"
                                                : "hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-600 dark:text-gray-400"
                                        )}
                                    >
                                        {pageNum}
                                    </button>
                                );
                            })}

                            <button
                                onClick={() => goToPage(currentPage + 1)}
                                disabled={!nextPageUrl}
                                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg disabled:opacity-30 disabled:cursor-not-allowed transition-colors text-gray-600 dark:text-gray-400"
                                title="Next page"
                            >
                                <ChevronRight className="w-4 h-4" />
                            </button>
                            <button
                                onClick={() => goToPage(totalPages)}
                                disabled={currentPage >= totalPages}
                                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg disabled:opacity-30 disabled:cursor-not-allowed transition-colors text-gray-600 dark:text-gray-400"
                                title="Last page"
                            >
                                <ChevronsRight className="w-4 h-4" />
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Sync Status Footer */}
            {lastSynced && (
                <div className="bg-gray-50 dark:bg-gray-900 border-t border-gray-100 dark:border-gray-800 p-2 px-8 flex justify-end">
                     <p className="text-[9px] uppercase font-black tracking-widest text-gray-400">
                        Agent last scanned at {format(lastSynced, 'PPP p')}
                     </p>
                </div>
            )}
        </div>
    );
};

const formatDateDense = (dateString) => {
    try {
        const date = new Date(dateString);
        if (isToday(date)) return format(date, 'h:mm a');
        if (isThisYear(date)) return format(date, 'MMM d');
        return format(date, 'MM/dd/yy');
    } catch (e) {
        return "";
    }
};

export default Inbox;