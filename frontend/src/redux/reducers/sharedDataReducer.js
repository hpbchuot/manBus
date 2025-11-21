// sharedDataReducer.js
import { SET_SHARED_DATA } from "../actions/index";

const initialState = { key1: "value1", key2: "value2" };

const sharedDataReducer = (state = initialState, action) => {
  switch (action.type) {
    case SET_SHARED_DATA:
      return { ...state, ...action.payload };
    default:
      return state;
  }
};

export default sharedDataReducer;
