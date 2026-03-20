import React, { useEffect, useState } from 'react';
import {
  Inbox,
  AlertTriangle,
  Lightbulb,
  Briefcase
} from 'lucide-react';
import { emailService, taskService } from '../services/api';
import StatCard from '../components/StatCard';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalEmails: 0,
    criticalEmails: 0,
    opportunityEmails: 0,
    pendingTasks: 0,
    categoryData: []
  });
  const [loading, setLoading] = useState(true);

  const fetchStats = async (showLoading = true) => {
    try {
      if (showLoading) setLoading(true);
      const [emailsRes, tasksRes] = await Promise.all([
        emailService.getAll({ limit: 1000 }),
        taskService.getAll({ reminder_sent: false })
      ]);

      const emails = emailsRes.data.results;
      const tasks = tasksRes.data.results;

      const critical = emails.filter(e => e.category === 'CRITICAL').length;
      const opportunity = emails.filter(e => e.category === 'OPPORTUNITY').length;
      const junk = emails.filter(e => e.category === 'JUNK').length;
      const info = emails.filter(e => e.category === 'INFO').length;

      setStats({
        totalEmails: emails.length,
        criticalEmails: critical,
        opportunityEmails: opportunity,
        pendingTasks: tasks.length,
        categoryData: [
          { name: 'Critical', count: critical, fill: '#ef4444' },
          { name: 'Opportunity', count: opportunity, fill: '#10b981' },
          { name: 'Info', count: info, fill: '#3b82f6' },
          { name: 'Junk', count: junk, fill: '#6b7280' },
        ]
      });
    } catch (error) {
      console.error("Failed to fetch dashboard stats", error);
    } finally {
      if (showLoading) setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();

    // Polling every 30 seconds for real-time updates
    const interval = setInterval(() => {
      fetchStats(false);
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Dashboard</h1>
        <div className="text-sm text-gray-500 dark:text-gray-400 font-medium bg-gray-100 dark:bg-gray-800 px-3 py-1 rounded-full uppercase tracking-widest text-[10px]">
          Anti-Anxiety Mode: ON
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {/* StatCards already handle dark mode */}
        <StatCard
          title="Total Emails"
          value={stats.totalEmails}
          icon={Inbox}
          color="indigo"
          href="/inbox"
        />
        <StatCard
          title="Critical Items"
          value={stats.criticalEmails}
          icon={AlertTriangle}
          color="red"
          href="/inbox?category=CRITICAL"
        />
        <StatCard
          title="Opportunities"
          value={stats.opportunityEmails}
          icon={Lightbulb}
          color="green"
          href="/inbox?category=OPPORTUNITY"
        />
        <StatCard
          title="Pending Tasks"
          value={stats.pendingTasks}
          icon={Briefcase}
          color="yellow"
          href="/tasks"
        />
      </div>

      {/* Charts Section */}
      <div className="bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-100 dark:border-gray-800 p-6 transition-all duration-300">
        <h2 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">Email Composition</h2>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={stats.categoryData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#374151" strokeOpacity={0.1} />
              <XAxis dataKey="name" stroke="#9ca3af" fontSize={12} tickLine={false} axisLine={false} />
              <YAxis stroke="#9ca3af" fontSize={12} tickLine={false} axisLine={false} />
              <Tooltip
                cursor={{ fill: 'transparent' }}
                contentStyle={{ 
                  backgroundColor: '#111827', 
                  borderRadius: '8px', 
                  border: 'none', 
                  color: '#f9fafb',
                  boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.3)' 
                }}
                itemStyle={{ color: '#f9fafb' }}
              />
              <Bar dataKey="count" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;