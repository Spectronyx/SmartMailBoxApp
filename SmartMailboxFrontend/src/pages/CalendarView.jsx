import React, { useState, useEffect } from 'react';
import { taskService } from '../services/api';
import { 
  ChevronLeft, 
  ChevronRight, 
  Calendar as CalendarIcon, 
  Download, 
  ExternalLink,
  Clock,
  CheckCircle,
  FileText
} from 'lucide-react';
import { 
  format, 
  addMonths, 
  subMonths, 
  startOfMonth, 
  endOfMonth, 
  startOfWeek, 
  endOfWeek, 
  isSameMonth, 
  isSameDay, 
  addDays, 
  eachDayOfInterval,
  parseISO
} from 'date-fns';
import { clsx } from 'clsx';
import { motion, AnimatePresence } from 'framer-motion';
import { Link } from 'react-router-dom';

const CalendarView = () => {
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        setLoading(true);
        const res = await taskService.getAll();
        setTasks(res.data.results.filter(t => t.deadline));
      } catch (error) {
        console.error("Failed to fetch tasks for calendar", error);
      } finally {
        setLoading(false);
      }
    };
    fetchTasks();
  }, []);

  const nextMonth = () => setCurrentMonth(addMonths(currentMonth, 1));
  const prevMonth = () => setCurrentMonth(subMonths(currentMonth, 1));

  const onDateClick = (day) => setSelectedDate(day);

  const renderHeader = () => (
    <div className="flex items-center justify-between mb-8 px-2">
      <div className="flex flex-col">
        <h2 className="text-3xl font-black text-gray-900 dark:text-gray-100 tracking-tighter">
          {format(currentMonth, 'MMMM yyyy')}
        </h2>
        <p className="text-[10px] text-gray-400 dark:text-gray-500 font-bold uppercase tracking-[0.2em] mt-1">
          {tasks.length} Active Deadlines
        </p>
      </div>
      <div className="flex items-center p-1 bg-white dark:bg-gray-900 rounded-xl border border-gray-100 dark:border-gray-800 shadow-sm">
        <button onClick={prevMonth} className="p-2 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-lg transition-colors text-gray-400 hover:text-indigo-600">
          <ChevronLeft className="w-5 h-5" />
        </button>
        <button onClick={() => setCurrentMonth(new Date())} className="px-4 py-2 text-xs font-black uppercase tracking-widest text-gray-500 hover:text-gray-900 dark:hover:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-lg transition-all">
          Today
        </button>
        <button onClick={nextMonth} className="p-2 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-lg transition-colors text-gray-400 hover:text-indigo-600">
          <ChevronRight className="w-5 h-5" />
        </button>
      </div>
    </div>
  );

  const renderDays = () => {
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    return (
      <div className="grid grid-cols-7 mb-2 border-b border-gray-100 dark:border-gray-800/50 pb-2">
        {days.map(day => (
          <div key={day} className="text-center text-[10px] font-black uppercase tracking-widest text-gray-400 dark:text-gray-600">
            {day}
          </div>
        ))}
      </div>
    );
  };

  const renderCells = () => {
    const monthStart = startOfMonth(currentMonth);
    const monthEnd = endOfMonth(monthStart);
    const startDate = startOfWeek(monthStart);
    const endDate = endOfWeek(monthEnd);

    const rows = [];
    let days = [];
    let day = startDate;
    let formattedDate = "";

    while (day <= endDate) {
      for (let i = 0; i < 7; i++) {
        formattedDate = format(day, 'd');
        const cloneDay = day;
        const dayTasks = tasks.filter(t => isSameDay(parseISO(t.deadline), cloneDay));
        
        days.push(
          <div
            key={day}
            className={clsx(
              "relative h-32 p-2 border border-gray-50 dark:border-gray-800/20 transition-all cursor-pointer",
              !isSameMonth(day, monthStart) ? "bg-gray-50/50 dark:bg-gray-950/50 opacity-30" : "bg-white dark:bg-gray-900/40 hover:bg-indigo-50/30 dark:hover:bg-indigo-900/10",
              isSameDay(day, new Date()) && "ring-1 ring-inset ring-indigo-500",
              isSameDay(day, selectedDate) && "bg-indigo-50/50 dark:bg-indigo-900/20"
            )}
            onClick={() => onDateClick(cloneDay)}
          >
            <span className={clsx(
              "text-xs font-black",
              isSameDay(day, new Date()) ? "text-indigo-600" : "text-gray-400",
              isSameMonth(day, monthStart) && !isSameDay(day, new Date()) && "dark:text-gray-600"
            )}>
              {formattedDate}
            </span>
            <div className="mt-1 space-y-1">
              {dayTasks.slice(0, 3).map(task => (
                <div 
                  key={task.id} 
                  className={clsx(
                    "px-1.5 py-0.5 rounded text-[8px] font-bold truncate transition-all",
                    task.is_completed 
                      ? "bg-gray-100 text-gray-400 dark:bg-gray-800 dark:text-gray-600 line-through" 
                      : "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800/50"
                  )}
                >
                  {task.action_text}
                </div>
              ))}
              {dayTasks.length > 3 && (
                <div className="text-[8px] font-bold text-gray-400 pl-1">
                  +{dayTasks.length - 3} more
                </div>
              )}
            </div>
          </div>
        );
        day = addDays(day, 1);
      }
      rows.push(
        <div className="grid grid-cols-7" key={day}>
          {days}
        </div>
      );
      days = [];
    }
    return <div className="bg-white dark:bg-gray-900 rounded-2xl overflow-hidden border border-gray-100 dark:border-gray-800 shadow-xl">{rows}</div>;
  };

  const renderSelectedDayTasks = () => {
    const dayTasks = tasks.filter(t => isSameDay(parseISO(t.deadline), selectedDate));
    
    return (
      <div className="mt-12">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-black text-gray-900 dark:text-gray-100 tracking-tight">
            Agenda for {format(selectedDate, 'MMMM do')}
          </h3>
          <button 
            onClick={() => window.open(taskService.exportCalendar(), '_blank')}
            className="flex items-center px-4 py-2 bg-white dark:bg-gray-900 text-gray-600 dark:text-gray-400 border border-gray-200 dark:border-gray-800 rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-gray-50 dark:hover:bg-gray-800 transition-all shadow-sm"
          >
            <Download className="w-3 h-3 mr-2" />
            Full iCal Export
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <AnimatePresence mode="popLayout">
            {dayTasks.length === 0 ? (
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="col-span-full py-12 text-center bg-white dark:bg-gray-900 rounded-2xl border border-dashed border-gray-200 dark:border-gray-800"
              >
                <p className="text-sm text-gray-400 font-medium">No tasks scheduled for this day.</p>
              </motion.div>
            ) : (
              dayTasks.map(task => (
                <motion.div
                  key={task.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  layout
                  className="bg-white dark:bg-gray-900 p-5 rounded-2xl border border-gray-100 dark:border-gray-800 shadow-sm flex flex-col justify-between group hover:border-indigo-200 dark:hover:border-indigo-800 transition-all"
                >
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className={clsx(
                        "px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-widest",
                        task.is_completed ? "bg-gray-100 text-gray-400" : "bg-indigo-50 text-indigo-600 dark:bg-indigo-900/30 dark:text-indigo-400"
                      )}>
                        {task.is_completed ? 'Completed' : 'Upcoming'}
                      </span>
                      <div className="flex items-center space-x-2">
                        <a 
                          href={taskService.exportIcs(task.id)} 
                          target="_blank" 
                          rel="noreferrer"
                          className="p-1.5 text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-900/30 rounded-lg transition-all"
                          title="Download ICS"
                        >
                          <Download className="w-4 h-4" />
                        </a>
                        <button
                          onClick={() => {
                            const date = format(parseISO(task.deadline), "yyyyMMdd'T'HHmmss'Z'");
                            const url = `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${encodeURIComponent(task.action_text)}&dates=${date}/${date}&details=${encodeURIComponent('From Smart Mailbox')}`;
                            window.open(url, '_blank');
                          }}
                          className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded-lg transition-all"
                          title="Add to Google Calendar"
                        >
                          <ExternalLink className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                    <h4 className={clsx("text-base font-bold leading-tight", task.is_completed ? "text-gray-400 line-through" : "text-gray-900 dark:text-gray-100")}>
                      {task.action_text}
                    </h4>
                    <Link 
                      to={`/emails/${task.email}`} 
                      className="mt-3 flex items-center text-[10px] font-black uppercase tracking-widest text-indigo-500 hover:text-indigo-700 transition-colors"
                    >
                      <FileText className="w-3 h-3 mr-1.5" />
                      View Context
                    </Link>
                  </div>
                  <div className="mt-4 pt-4 border-t border-gray-50 dark:border-gray-800 flex items-center text-[10px] text-gray-400 dark:text-gray-500 font-bold uppercase tracking-widest">
                    <Clock className="w-3 h-3 mr-1.5" />
                    {format(parseISO(task.deadline), 'h:mm a')}
                  </div>
                </motion.div>
              ))
            )}
          </AnimatePresence>
        </div>
      </div>
    );
  };

  return (
    <div className="max-w-6xl mx-auto py-4">
      {renderHeader()}
      {renderDays()}
      {renderCells()}
      {renderSelectedDayTasks()}
    </div>
  );
};

export default CalendarView;
