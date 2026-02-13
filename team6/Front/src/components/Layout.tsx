import { Outlet, NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {
  LayoutDashboard,
  SpellCheck,
  LineChart,
  LogOut,
  User,
  BookOpen,
} from "lucide-react";

export default function Layout() {
  const { logout, userId } = useAuth();

  const navItems = [
    { name: "Dashboard", path: "/", icon: LayoutDashboard },
    { name: "Grammar Check", path: "/check", icon: SpellCheck },
    { name: "My Progress", path: "/stats", icon: LineChart },
    { name: "Exercises", path: "/exercises", icon: BookOpen },
  ];

  return (
    <div className="min-h-screen bg-bg-main flex font-sans text-dark-900">
      {/* --- Sidebar --- */}
      <aside className="w-64 bg-white border-r border-gray-200 fixed h-full z-10 hidden md:flex flex-col">
        <div className="h-16 flex items-center px-8 border-b border-gray-100">
          <div className="flex items-center gap-2 text-primary font-bold text-xl">
            <SpellCheck className="w-8 h-8" />
            <span>GrammarAI</span>
          </div>
        </div>

        <nav className="flex-1 px-4 py-6 space-y-2">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-xl transition-colors duration-200 ${
                  isActive
                    ? "bg-primary-light text-primary font-medium"
                    : "text-gray-500 hover:bg-gray-50 hover:text-dark-900"
                }`
              }
            >
              <item.icon size={20} />
              {item.name}
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-gray-100">
          <button
            onClick={logout}
            className="flex items-center gap-3 px-4 py-3 w-full text-left text-red-500 hover:bg-red-50 rounded-xl transition-colors"
          >
            <LogOut size={20} />
            Logout
          </button>
        </div>
      </aside>

      {/* --- Main Content --- */}
      <div className="flex-1 md:ml-64 flex flex-col min-h-screen">
        {/* Header */}
        <header className="h-16 bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-20 px-8">
          <div className="max-w-7xl mx-auto h-full flex items-center justify-between">
            <h2 className="text-lg font-semibold text-dark-800">
              Welcome Back!
            </h2>

            <div className="flex items-center gap-4">
              <div className="flex items-center gap-3 pl-4 border-l border-gray-200">
                <div className="text-right hidden sm:block">
                  <p className="text-sm font-medium text-dark-900">
                    User {userId}
                  </p>
                  <p className="text-xs text-gray-500">Computer Engineer</p>
                </div>
                <div className="w-10 h-10 bg-secondary-light text-secondary rounded-full flex items-center justify-center">
                  <User size={20} />
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="p-8 flex-1 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
