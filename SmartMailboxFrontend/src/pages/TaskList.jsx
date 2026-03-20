import React, { useEffect, useState } from 'react';
import { taskService } from '../services/api';
import {
  Clock,
  CheckCircle,
  Bell
} from 'lucide-react';
import { format, isPast, isToday, addDays } from 'date-fns';
import { clsx } from 'clsx';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';

const TaskList = () => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [triggering, setTriggering] = useState(false);
  const [expandedTasks, setExpandedTasks] = useState({});

  const fetchTasks = async (showLoading = true) => {
    try {
      if (showLoading) setLoading(true);
      const response = await taskService.getAll();
      setTasks(response.data.results);
    } catch (error) {
      console.error("Failed to fetch tasks", error);
    } finally {
      if (showLoading) setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
    const interval = setInterval(() => fetchTasks(false), 30000);
    return () => clearInterval(interval);
  }, []);

  const toggleExpand = (taskId) => {
    setExpandedTasks(prev => ({
      ...prev,
      [taskId]: !prev[taskId]
    }));
  };

  const handleRunReminders = async () => {
    try {
      setTriggering(true);
      const res = await taskService.runReminders();
      alert(res.data.message);
      fetchTasks();
    } catch (error) {
      console.error("Reminder trigger failed", error);
    } finally {
      setTriggering(false);
    }
  };

  const handleToggleComplete = async (taskId, currentStatus) => {
    try {
      // Optimistic UI update
      setTasks(prev => prev.map(t => 
        t.id === taskId ? { ...t, is_completed: !currentStatus } : t
      ).sort((a, b) => {
        if (a.is_completed !== b.is_completed) return a.is_completed ? 1 : -1;
        return new Date(a.deadline || 0) - new Date(b.deadline || 0);
      }));

      await taskService.update(taskId, { is_completed: !currentStatus });
    } catch (error) {
      console.error("Failed to toggle task", error);
      fetchTasks(false);
    }
  };

  const getUrgencyColor = (deadline, is_completed) => {
    if (is_completed) return "bg-gray-100 dark:bg-gray-800 text-gray-400 dark:text-gray-500";
    if (!deadline) return "bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400";
    const date = new Date(deadline);
    if (isPast(date) && !isToday(date)) return "bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300";
    if (isToday(date)) return "bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-300";
    if (date <= addDays(new Date(), 3)) return "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300";
    return "bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300";
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 tracking-tight">Task Tracker</h1>
        <button
          onClick={handleRunReminders}
          disabled={triggering}
          className="flex items-center px-4 py-2 bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 rounded-lg hover:bg-indigo-200 dark:hover:bg-indigo-900/50 transition-colors font-medium border border-indigo-200 dark:border-indigo-800"
        >
          <Bell className={clsx("w-4 h-4 mr-2", triggering && "animate-spin")} />
          Check Reminders
        </button>
      </div>

      <div className="bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-100 dark:border-gray-800 overflow-hidden transition-all duration-300">
        {loading ? (
          <div className="p-24 text-center">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600 mx-auto"></div>
            <p className="mt-4 text-sm text-gray-500 dark:text-gray-400 font-medium">Loading tasks...</p>
          </div>
        ) : tasks.length === 0 ? (
          <div className="p-24 text-center text-gray-500 dark:text-gray-400 font-medium italic">
            No tasks found. Relax!
          </div>
        ) : (
          <div className="divide-y divide-gray-100 dark:divide-gray-800">
            <AnimatePresence mode="popLayout">
              {tasks.map((task) => (
                <motion.div 
                  layout
                  initial={{ opacity: 0, scale: 0.98 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  key={task.id} 
                  className={clsx(
                    "p-4 sm:px-6 hover:bg-gray-50 dark:hover:bg-gray-800/30 transition-colors group",
                    task.is_completed && "opacity-60 bg-gray-50/50 dark:bg-gray-800/20"
                  )}
                >
                  <div className="flex flex-col">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-4 w-full">
                        <button
                          onClick={() => handleToggleComplete(task.id, task.is_completed)}
                          className="mt-1 flex-shrink-0 focus:outline-none transition-transform active:scale-90"
                          title={task.is_completed ? "Mark as incomplete" : "Mark as complete"}
                        >
                          {task.is_completed ? (
                            <CheckCircle className="w-6 h-6 text-green-500 dark:text-green-400 fill-green-50 dark:fill-green-900/20" />
                          ) : (
                            <div className="w-6 h-6 border-2 border-gray-300 dark:border-gray-600 rounded-md hover:border-indigo-400 dark:hover:border-indigo-500 transition-colors bg-white dark:bg-gray-800 shadow-sm" />
                          )}
                        </button>
                        <div className="flex-1 min-w-0">
                          <h3 className={clsx(
                            "text-base font-bold transition-all duration-300",
                            task.is_completed ? "text-gray-400 dark:text-gray-600 line-through decoration-gray-300 dark:decoration-gray-700" : "text-gray-900 dark:text-gray-100"
                          )}>
                            {task.action_text}
                          </h3>
                          <div className="mt-1.5 flex flex-wrap items-center gap-x-4 gap-y-2 text-sm text-gray-500 dark:text-gray-400">
                            {task.deadline && (
                              <span className={clsx(
                                "flex items-center px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-widest",
                                getUrgencyColor(task.deadline, task.is_completed)
                              )}>
                                <Clock className="w-3 h-3 mr-1" />
                                {format(new Date(task.deadline), 'MMM d, h:mm a')}
                              </span>
                            )}
                            {task.email_detail && (
                              <div className="flex items-center space-x-2">
                                <span className="text-xs text-gray-300 dark:text-gray-700 hidden sm:inline">|</span>
                                <Link to={`/emails/${task.email_detail.id}`} className="hover:text-indigo-600 dark:hover:text-indigo-400 font-bold transition-colors">
                                  {(task.email_detail.subject || "").substring(0, 30)}...
                                </Link>
                                <button
                                  onClick={() => toggleExpand(task.id)}
                                  className="text-indigo-500 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 text-[10px] font-black uppercase tracking-widest flex items-center ml-2"
                                >
                                  {expandedTasks[task.id] ? "Hide" : "Story"}
                                </button>
                              </div>
                            )}
                            {task.reminder_sent && !task.is_completed && (
                              <span className="flex items-center text-orange-600 dark:text-orange-400 text-[10px] font-black uppercase bg-orange-50 dark:bg-orange-900/20 px-2 py-0.5 rounded tracking-widest">
                                <Bell className="w-3 h-3 mr-1" />
                                Sent
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>

                    <AnimatePresence>
                      {expandedTasks[task.id] && task.email_detail && (
                        <motion.div 
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: "auto", opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          className="overflow-hidden"
                        >
                          <div className="mt-4 ml-10 p-5 bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-gray-100 dark:border-gray-800 text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap font-sans shadow-inner">
                            <div className="mb-2 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.2em]">Context</div>
                            {task.email_detail.body || "No content available."}
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
      </div>
    </div>
  );
};

export default TaskList;