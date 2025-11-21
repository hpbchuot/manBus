export const controlLoading = (status) => {
  return {
    type: "CONTROL_LOADING",
    status,
  };
};
// actions.js
export const SET_SHARED_DATA = "SET_SHARED_DATA";

export const setSharedData = (data) => ({
  type: SET_SHARED_DATA,
  payload: data,
});
