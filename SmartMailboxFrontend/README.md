# Smart Mailbox Frontend

A premium React dashboard for intelligent email management, built with speed and aesthetics in mind.

## ✨ Highlights

- **Dynamic Theming**: True Dark Mode with `ThemeContext` and system synchronization.
- **Interactive UI**: Fluid micro-animations powered by **Framer Motion**.
- **Unified Inbox**: High-performance email list with advanced filtering and search.
- **Task Calendar**: A comprehensive monthly view for managing AI-extracted deadlines.
- **Responsive Navigation**: Sidebar for desktop and a sleek header for mobile views.

## 🛠️ Tech Stack

- **React 19**: Using the latest concurrent features.
- **Tailwind CSS 4**: Modern, utility-first styling.
- **Framer Motion**: For all UI transitions and entry animations.
- **Lucide Icons**: Crisp, themed iconography.
- **Date-fns**: Robust date manipulation and formatting.

## 🚀 Local Development

```bash
npm install
npm run dev
```

## 📂 Structure
- `/src/pages`: CalendarView, Inbox, TaskList, EmailDetail, Dashboard.
- `/src/context`: Theme and Auth providers.
- `/src/components`: UI components (StatCards, Modals, Navigation).
- `/src/services`: API abstraction layer.
