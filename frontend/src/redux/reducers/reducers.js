import { combineReducers } from "redux";
import globalLoading from "./globalLoading";
import sharedDataReducer from "./sharedDataReducer";

const appReducers = combineReducers({
  globalLoading,
  mapSearch: sharedDataReducer,
});

export default appReducers;
