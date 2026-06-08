import { create } from "zustand";
import { persist } from "zustand/middleware";
import { decodeToken } from "../utils/jwt";

const useAuthStore = create(
  persist(
    (set) => ({
      token: null,
      user: null,
      login: (token, email) => {
        const decoded = decodeToken(token);
        set({
          token,
          user: { id: decoded.id, role: decoded.role, email },
        });
      },
      logout: () => set({ token: null, user: null }),
    }),
    { name: "auth-storage" }
  )
);

export default useAuthStore;
