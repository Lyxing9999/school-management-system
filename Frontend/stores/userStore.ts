import type { User } from "~/types/models/User";
import { UserService } from "~/services/userService";
import { UserModel } from "~/models/userModel";
import type { UserDetail } from "~/types/userServiceInterface";
import { UserStoreError } from "~/errors/UserStoreError";
import { unflatten } from "~/utils/unflatten";
import { convertDatesToISOString } from "~/utils/convertDatesToISOString";
import type { AxiosInstance } from "axios";
export const useUserStore = defineStore("user", () => {
  const $api = useNuxtApp().$api as AxiosInstance;
  const userService = new UserService($api);
  const loadingUserDetails = reactive<Record<string, boolean>>({});
  const users = ref<User[]>([]);
  const userDetailsCache = reactive<Record<string, UserDetail>>({});
  const loadingStates = reactive<{ fetchUsers: boolean }>({
    fetchUsers: false,
  });

  const fetchUsers = async (): Promise<User[]> => {
    if (loadingStates.fetchUsers) {
      return users.value;
    }

    loadingStates.fetchUsers = true;

    try {
      const usersArray = await userService.listUsers();
      users.value = usersArray.map((user) => new UserModel(user));
      console.log("users", users.value);
      return users.value;
    } catch (error) {
      if (error instanceof UserStoreError) {
        throw error;
      } else {
        throw new UserStoreError(
          "Failed to fetch users",
          "FETCH_USERS_FAILED",
          error
        );
      }
    } finally {
      loadingStates.fetchUsers = false;
    }
  };

  const getUserDetails = async (id: string): Promise<UserDetail | null> => {
    if (userDetailsCache[id]) return userDetailsCache[id];
    if (loadingUserDetails[id]) {
      throw new UserStoreError(
        "Already loading user details...",
        "ALREADY_LOADING_USER_DETAILS",
        null
      );
    }

    loadingUserDetails[id] = true;

    try {
      const userDetail = await userService.getUserDetails(id);

      if (!userDetail) {
        throw new UserStoreError(
          `No user details found for id ${id}`,
          "USER_NOT_FOUND",
          null
        );
      }
      userDetailsCache[id] = userDetail;
      return userDetail;
    } catch (error) {
      if (error instanceof UserStoreError) {
        throw error;
      } else {
        throw new UserStoreError(
          "Failed to fetch user details",
          "FETCH_USER_DETAILS_FAILED",
          error
        );
      }
    } finally {
      delete loadingUserDetails[id];
    }
  };
  const clearUserDetailsCache = (id?: string) => {
    if (id) {
      delete userDetailsCache[id];
    } else {
      Object.keys(userDetailsCache).forEach(
        (key) => delete userDetailsCache[key]
      );
    }
  };

  const updateUserPatch = async (
    userId: string,
    flatData: Partial<UserDetail>
  ) => {
    try {
      const nestedData = unflatten(flatData);
      const finalData = convertDatesToISOString(nestedData);
      const res = await userService.editUserDetail(
        userId,
        finalData as unknown as UserDetail
      );
      if (!res.status) {
        console.error(
          "Update failed with status:",
          res.status,
          "and message:",
          res.msg
        );
        throw new UserStoreError(
          "Failed to update user details",
          "UPDATE_USER_DETAILS_FAILED",
          null
        );
      }
      return res; // or return res.msg if you want
    } catch (error) {
      if (error instanceof UserStoreError) {
        throw error;
      } else {
        throw new UserStoreError(
          "Failed to update user details",
          "UPDATE_USER_DETAILS_FAILED",
          error
        );
      }
    }
  };

  return {
    users,
    loadingStates,
    fetchUsers,
    getUserDetails,
    clearUserDetailsCache,
    updateUserPatch,
  };
});
