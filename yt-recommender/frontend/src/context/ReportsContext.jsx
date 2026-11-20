import { createContext, useContext, useState, useEffect } from 'react';
import { useAuth } from './AuthContext';

const ReportsContext = createContext();

export const useReports = () => {
    const context = useContext(ReportsContext);
    if (!context) {
        throw new Error('useReports must be used within ReportsProvider');
    }
    return context;
};

export const ReportsProvider = ({ children }) => {
    const { user } = useAuth();
    const [reports, setReports] = useState([]);

    // Get current storage key: user-specific if logged in, or guest storage
    const getStorageKey = () => (user?.user_id ? `reports_${user.user_id}` : 'reports_guest');

    // Load reports for current user or guest
    useEffect(() => {
        const storageKey = getStorageKey();
        console.log('[ReportsContext] Loading reports from key:', storageKey);
        const savedReports = localStorage.getItem(storageKey);

        if (savedReports) {
            try {
                const parsed = JSON.parse(savedReports);
                console.log('[ReportsContext] Loaded reports:', parsed.length);
                setReports(parsed);
            } catch (error) {
                console.error('Failed to parse reports:', error);
                setReports([]);
            }
        } else {
            // Check legacy 'reports' key
            const oldReports = localStorage.getItem('reports');
            if (oldReports) {
                try {
                    const parsedOldReports = JSON.parse(oldReports);
                    console.log('[ReportsContext] Migrating old reports:', parsedOldReports.length);
                    setReports(parsedOldReports);
                    localStorage.setItem(storageKey, oldReports);
                    localStorage.removeItem('reports');
                } catch (error) {
                    console.error('Failed to migrate old reports:', error);
                    setReports([]);
                }
            } else {
                setReports([]);
            }
        }
    }, [user?.user_id]);

    // Save reports to localStorage whenever they change
    useEffect(() => {
        const storageKey = getStorageKey();
        console.log('[ReportsContext] Saving reports:', reports.length, 'to key:', storageKey);
        localStorage.setItem(storageKey, JSON.stringify(reports));
    }, [reports, user?.user_id]);

    const addReport = (report) => {
        setReports((prev) => [report, ...prev]);
    };

    const getReport = (id) => {
        // Primary lookup in current state
        const found = reports.find((report) => report.id === id);
        if (found) return found;
        // Fallback: try to read from localStorage
        try {
            const storageKey = getStorageKey();
            const saved = localStorage.getItem(storageKey);
            if (saved) {
                const parsed = JSON.parse(saved);
                return parsed.find((r) => r.id === id);
            }
        } catch (e) {
            console.error('Error reading reports from storage for fallback', e);
        }
        return undefined;
    };

    const deleteReport = (id) => {
        setReports((prev) => prev.filter((report) => report.id !== id));
    };

    const clearReports = () => {
        setReports([]);
        const storageKey = getStorageKey();
        localStorage.removeItem(storageKey);
    };

    const value = {
        reports,
        addReport,
        getReport,
        deleteReport,
        clearReports,
    };

    return <ReportsContext.Provider value={value}>{children}</ReportsContext.Provider>;
};
