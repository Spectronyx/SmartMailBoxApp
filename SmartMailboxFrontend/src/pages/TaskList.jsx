import React, { useEffect, useState } from 'react';
import { taskService } from '../services/api';
import {
  CheckSquare,
  Clock,
  AlertTriangle,
  Calendar,
  CheckCircle,
  Bell
} from 'lucide-react';
import { format, isPast, isToday, addDays } from 'date-fns';
import { clsx } from 'clsx';
import { Link } from 'react-router-dom';

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

    // Simple polling for "real-time" updates (every 30s)
    const interval = setInterval(() => {
      fetchTasks(false);
    }, 30000);

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

  const getUrgencyColor = (deadline) => {
    if (!deadline) return "bg-gray-100 text-gray-600";
    const date = new Date(deadline);
    if (isPast(date) && !isToday(date)) return "bg-red-100 text-red-800"; // Overdue
    if (isToday(date)) return "bg-orange-100 text-orange-800"; // Due today
    if (date <= addDays(new Date(), 3)) return "bg-yellow-100 text-yellow-800"; // Due soon
    return "bg-green-100 text-green-800"; // Upcoming
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Task Tracker</h1>
        <button
          onClick={handleRunReminders}
          disabled={triggering}
          className="flex items-center px-4 py-2 bg-indigo-100 text-indigo-700 rounded-lg hover:bg-indigo-200 transition-colors"
        >
          <Bell className={clsx("w-4 h-4 mr-2", triggering && "animate-spin")} />
          Check Reminders
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        {loading ? (
          <div className="p-12 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto"></div>
          </div>
        ) : tasks.length === 0 ? (
          <div className="p-12 text-center text-gray-500">
            No tasks found. Relax!
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {tasks.map((task) => (
              <div key={task.id} className="p-4 sm:px-6 hover:bg-gray-50 transition-colors group">
                <div className="flex flex-col">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-4">
                      <div className="mt-1">
                        <CheckSquare className="w-5 h-5 text-gray-400" />
                      </div>
                      <div>
                        <h3 className="text-base font-medium text-gray-900">{task.action_text}</h3>
                        <div className="mt-1 flex items-center space-x-4 text-sm text-gray-500">
                          {task.deadline && (
                            <span className={clsx(
                              "flex items-center px-2 py-0.5 rounded text-xs font-semibold uppercase tracking-wide",
                              getUrgencyColor(task.deadline)
                            )}>
                              <Clock className="w-3 h-3 mr-1" />
                              {format(new Date(task.deadline), 'MMM d, h:mm a')}
                            </span>
                          )}
                          {task.email_detail && (
                            <div className="flex items-center space-x-2">
                              <span className="text-xs text-gray-400">|</span>
                              <Link to={`/emails/${task.email_detail.id}`} className="hover:text-indigo-600 font-medium">
                                Email: {(task.email_detail.subject || "").substring(0, 30)}...
                              </Link>
                              <button
                                onClick={() => toggleExpand(task.id)}
                                className="text-indigo-500 hover:text-indigo-700 text-xs flex items-center"
                              >
                                {expandedTasks[task.id] ? "Hide Message" : "View Message"}
                              </button>
                            </div>
                          )}
                          {task.reminder_sent && (
                            <span className="flex items-center text-orange-600 text-xs font-medium bg-orange-50 px-2 py-0.5 rounded">
                              <Bell className="w-3 h-3 mr-1" />
                              Reminder Sent
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Expandable Email Body */}
                  {expandedTasks[task.id] && task.email_detail && (
                    <div className="mt-4 ml-9 p-4 bg-gray-50 rounded-lg border border-gray-100 text-sm text-gray-700 whitespace-pre-wrap font-sans">
                      <div className="mb-2 text-xs font-bold text-gray-400 uppercase tracking-widest">Original Email Content</div>
                      {task.email_detail.body || "No content available."}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default TaskList;