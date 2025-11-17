// hooks/useDrivers.js
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import requestApi from "../helpers/api";
import { toast } from "react-toastify";

export const useDrivers = (page = 0, pageSize = 10) => {
  return useQuery({
    queryKey: ["drivers", page, pageSize],
    queryFn: async () => {
      const response = await requestApi("/manager/get-all-driver", "GET");
      return response.data;
    },
  });
};
export const useBusInDriver = () => {
  return useQuery({
    queryKey: ["buses"],
    queryFn: async () => {
      const response = await requestApi("/bus/get-all-bus", "GET");
      return response.data;
    },
  });
};

export const useCreateDriver = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data) => requestApi("/manager/create-driver", "POST", data),
    onSuccess: () => {
      queryClient.invalidateQueries(["drivers"]);
      toast.success("Tạo tài xế thành công!");
    },
    onError: (error) => {
      toast.error(error.response?.data?.message || "Có lỗi xảy ra!");
    },
  });
};

export const useUpdateDriver = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data) => requestApi("/manager/update-driver", "POST", data),
    onSuccess: () => {
      queryClient.invalidateQueries(["drivers"]);
      toast.success("Cập nhật tài xế thành công!");
    },
    onError: (error) => {
      toast.error(error.response?.data?.message || "Có lỗi xảy ra!");
    },
  });
};

export const useDeleteDriver = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data) => requestApi("/manager/delete-driver", "POST", data),
    onSuccess: () => {
      queryClient.invalidateQueries(["drivers"]);
      toast.success("Xóa tài xế thành công!");
    },
    onError: (error) => {
      toast.error(error.response?.data?.message || "Có lỗi xảy ra!");
    },
  });
};
