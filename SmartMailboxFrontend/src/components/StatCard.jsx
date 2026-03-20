import React from 'react';
import { clsx } from 'clsx';
import { ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

const StatCard = ({ title, value, icon: Icon, color = "indigo", href }) => {
    const colorStyles = {
        indigo: "bg-indigo-50 text-indigo-700",
        red: "bg-red-50 text-red-700",
        green: "bg-green-50 text-green-700",
        yellow: "bg-yellow-50 text-yellow-700",
        blue: "bg-blue-50 text-blue-700",
    };

    return (
        <div className="bg-white overflow-hidden shadow-sm rounded-xl border border-gray-100 hover:shadow-md transition-shadow">
            <div className="p-5">
                <div className="flex items-center">
                    <div className={clsx("flex-shrink-0 p-3 rounded-lg", colorStyles[color])}>
                        <Icon className="h-6 w-6" />
                    </div>
                    <div className="ml-5 w-0 flex-1">
                        <dl>
                            <dt className="text-sm font-medium text-gray-500 truncate">{title}</dt>
                            <dd>
                                <div className="text-2xl font-bold text-gray-900">{value}</div>
                            </dd>
                        </dl>
                    </div>
                </div>
            </div>
            {href && (
                <div className="bg-gray-50 px-5 py-3">
                    <Link to={href} className="text-sm font-medium text-indigo-600 hover:text-indigo-900 flex items-center">
                        View details
                        <ArrowRight className="ml-1 h-4 w-4" />
                    </Link>
                </div>
            )}
        </div>
    );
};

export default StatCard;
