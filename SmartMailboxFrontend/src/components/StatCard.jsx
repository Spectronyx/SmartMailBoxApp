import React from 'react';
import { clsx } from 'clsx';
import { ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

const StatCard = ({ title, value, icon: Icon, color = "indigo", href }) => {
    const colorStyles = {
        indigo: "bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300",
        red: "bg-red-50 dark:bg-red-900/30 text-red-700 dark:text-red-300",
        green: "bg-green-50 dark:bg-green-900/30 text-green-700 dark:text-green-300",
        yellow: "bg-yellow-50 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300",
        blue: "bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300",
    };

    return (
        <div className="bg-white dark:bg-gray-900 overflow-hidden shadow-sm rounded-xl border border-gray-100 dark:border-gray-800 hover:shadow-md transition-all duration-300">
            <div className="p-5">
                <div className="flex items-center">
                    <div className={clsx("flex-shrink-0 p-3 rounded-lg", colorStyles[color])}>
                        <Icon className="h-6 w-6" />
                    </div>
                    <div className="ml-5 w-0 flex-1">
                        <dl>
                            <dt className="text-sm font-medium text-gray-400 truncate">{title}</dt>
                            <dd>
                                <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">{value}</div>
                            </dd>
                        </dl>
                    </div>
                </div>
            </div>
            {href && (
                <div className="bg-gray-50 dark:bg-gray-800/50 px-5 py-3 border-t border-gray-50 dark:border-gray-800">
                    <Link to={href} className="text-sm font-medium text-indigo-600 dark:text-indigo-400 hover:text-indigo-900 dark:hover:text-indigo-200 flex items-center transition-colors">
                        View details
                        <ArrowRight className="ml-1 h-4 w-4" />
                    </Link>
                </div>
            )}
        </div>
    );
};

export default StatCard;
