import React, { createContext, useContext, useState } from "react";
import axios from "axios";

const AuthContext = createContext();

// Backend URL from env
const API = import.meta.env.VITE_API_URL;

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem("token"));

    // ================= REGISTER =================
    const register = async (data) => {
        try {
            const response = await axios.post(
                `${API}/api/v1/auth/register`,
                data
            );
            return response.data;
        } catch (error) {
            throw error;
        }
    };

    // ================= LOGIN =================
    const login = async (data) => {
        try {
            const response = await axios.post(
                `${API}/api/v1/auth/login`,
                data
            );

            const accessToken = response.data.access_token;

            setToken(accessToken);
            localStorage.setItem("token", accessToken);

            // optional: fetch user profile if you have endpoint
            setUser(response.data.user || null);

            return response.data;
        } catch (error) {
            throw error;
        }
    };

    // ================= LOGOUT =================
    const logout = () => {
        setUser(null);
        setToken(null);
        localStorage.removeItem("token");
    };

    return (
        <AuthContext.Provider
            value={{
                user,
                token,
                register,
                login,
                logout,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
};

// Hook
export const useAuth = () => useContext(AuthContext);
