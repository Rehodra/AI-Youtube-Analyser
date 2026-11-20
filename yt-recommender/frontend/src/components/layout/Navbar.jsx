import { useState, useEffect, useRef } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Youtube, LogOut, Menu, X, FileText, ChevronDown, BarChart3, User } from "lucide-react";

const Navbar = ({ isLoggedIn, user, onLogout }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [profileDropdownOpen, setProfileDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setProfileDropdownOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const navLinks = [
    { id: "platform", label: "Platform", path: "/" },
    { id: "solutions", label: "Solutions", path: "/solutions" },
    { id: "pricing", label: "Pricing", path: "/pricing" },
    { id: "about", label: "About", path: "/about" },
  ];

  const isActive = (path) => {
    if (path === "/" && location.pathname === "/") return true;
    if (path !== "/" && location.pathname.startsWith(path)) return true;
    return false;
  };

  const getInitials = (name) => {
    if (!name) return "U";
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  };

  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 bg-white border-b border-slate-200 ${scrolled ? 'shadow-md py-4' : 'shadow-sm py-5'}`}>
      <div className="max-w-screen-2xl mx-auto px-6 lg:px-12">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 group">
            <div className="p-2 bg-slate-900 rounded-lg text-white">
              <Youtube size={20} strokeWidth={2.5} />
            </div>
            <span className="font-bold text-xl tracking-tight text-slate-900">
              Tube<span className="text-sky-600">Intelligence</span>
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden lg:flex items-center gap-8">
            {navLinks.map((link) => (
              <Link
                key={link.id}
                to={link.path}
                className={`text-sm font-medium transition-colors ${isActive(link.path)
                  ? "text-sky-600 font-semibold"
                  : "text-slate-600 hover:text-slate-900"
                  }`}
              >
                {link.label}
              </Link>
            ))}
          </div>

          {/* Actions */}
          <div className="flex items-center gap-4">
            <Link
              to="/audit"
              className="flex items-center gap-2 px-4 py-2 bg-slate-900 text-white text-sm font-medium rounded-lg hover:bg-slate-800 transition-all shadow-sm"
            >
              <BarChart3 size={18} />
              <span>Audit Channel</span>
            </Link>

            {!isLoggedIn ? (
              <>
                <Link
                  to="/reports"
                  className="hidden sm:flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-slate-700 hover:text-slate-900 transition-colors"
                >
                  <FileText size={16} className="text-slate-400" />
                  <span>Reports</span>
                </Link>
                <Link
                  to="/login"
                  className="hidden sm:block px-4 py-2 text-sm font-medium text-slate-700 hover:text-slate-900 transition-colors"
                >
                  Log in
                </Link>
                <Link
                  to="/register"
                  className="px-4 py-2 bg-slate-100 text-slate-800 text-sm font-medium rounded-lg hover:bg-slate-200 transition-all shadow-sm"
                >
                  Get Started
                </Link>
              </>
            ) : (
              <>
                <div className="hidden md:flex items-center gap-2">
                  <Link
                    to="/reports"
                    className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 rounded-lg transition-all"
                  >
                    <FileText size={18} className="text-slate-400" />
                    <span>Reports</span>
                  </Link>
                </div>

                {/* Profile Dropdown */}
                <div className="relative" ref={dropdownRef}>
                  <button
                    onClick={() => setProfileDropdownOpen(!profileDropdownOpen)}
                    className="flex items-center gap-3 px-2 py-1 hover:bg-slate-50 rounded-lg transition-all border border-transparent hover:border-slate-200"
                  >
                    {user?.avatar_url ? (
                      <img
                        src={user.avatar_url}
                        alt={user.username}
                        className="w-8 h-8 rounded-full object-cover ring-2 ring-slate-100"
                      />
                    ) : (
                      <div className="w-8 h-8 rounded-full bg-slate-900 flex items-center justify-center text-white text-xs font-bold ring-2 ring-slate-100">
                        {getInitials(user?.full_name || user?.username)}
                      </div>
                    )}
                    <ChevronDown size={14} className={`text-slate-400 transition-transform ${profileDropdownOpen ? 'rotate-180' : ''}`} />
                  </button>

                  {/* Dropdown Menu */}
                  {profileDropdownOpen && (
                    <div className="absolute right-0 mt-2 w-64 bg-white rounded-xl shadow-xl border border-slate-200 py-1 animate-slideDown origin-top-right ring-1 ring-black/5 z-50">
                      <div className="px-4 py-3 border-b border-slate-100">
                        <p className="font-semibold text-slate-900">{user?.full_name || user?.username}</p>
                        <p className="text-sm text-slate-500 truncate">{user?.email}</p>
                      </div>

                      <div className="py-1">
                        <div className="px-4 py-2">
                          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Plan</div>
                          <div className="flex items-center justify-between">
                            <span className="text-sm font-medium text-slate-700 capitalize">{user?.plan}</span>
                            <Link to="/pricing" className="text-xs text-sky-600 hover:underline">Upgrade</Link>
                          </div>
                        </div>
                        <div className="border-t border-slate-100 my-1"></div>
                        <Link
                          to="/reports"
                          onClick={() => setProfileDropdownOpen(false)}
                          className="flex items-center gap-3 px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 transition-colors md:hidden"
                        >
                          <FileText size={16} className="text-slate-400" />
                          <span>Reports</span>
                        </Link>
                        <Link
                          to="/audit"
                          onClick={() => setProfileDropdownOpen(false)}
                          className="flex items-center gap-3 px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 transition-colors md:hidden"
                        >
                          <BarChart3 size={16} className="text-slate-400" />
                          <span>New Audit</span>
                        </Link>
                      </div>

                      <div className="border-t border-slate-100 pt-1 pb-1">
                        <Link
                          to="/profile"
                          onClick={() => setProfileDropdownOpen(false)}
                          className="flex items-center gap-3 px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 transition-colors"
                        >
                          <User size={16} className="text-slate-400" />
                          <span>Profile</span>
                        </Link>
                        <button
                          onClick={() => {
                            setProfileDropdownOpen(false);
                            onLogout();
                          }}
                          className="flex items-center gap-3 px-4 py-2 text-red-600 hover:bg-red-50 transition-colors w-full text-sm"
                        >
                          <LogOut size={16} />
                          <span>Sign out</span>
                        </button>
                      </div>
                    </div>
                  )}

                </div>
              </>
            )}

            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden p-2 text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
            >
              {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="lg:hidden py-4 border-t border-slate-100 animate-slideDown">
            {navLinks.map((link) => (
              <Link
                key={link.id}
                to={link.path}
                onClick={() => setMobileMenuOpen(false)}
                className={`block px-4 py-3 rounded-lg text-sm font-medium transition-colors ${isActive(link.path)
                  ? "bg-slate-50 text-sky-600"
                  : "text-slate-600 hover:bg-slate-50"
                  }`}
              >
                {link.label}
              </Link>
            ))}
          </div>
        )}
      </div>


    </nav>
  );
};

export default Navbar;
