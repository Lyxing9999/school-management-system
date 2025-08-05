// composables/useMessage.ts
import { ElMessage } from 'element-plus'

export function useMessage() {
  /**
   * Show a success message toast
   * @param msg - Message text to display
   */
  function showSuccess(msg: string) {
    ElMessage({
      message: msg,
      type: 'success',
      duration: 3000,
      showClose: true,
    })
  }

  /**
   * Show an error message toast
   * @param msg - Message text to display
   */
  function showError(msg: string) {
    ElMessage({
      message: msg,
      type: 'error',
      duration: 5000,
      showClose: true,
    })
  }

  /**
   * Show an info message toast
   * @param msg - Message text to display
   */
  function showInfo(msg: string) {
    ElMessage({
      message: msg,
      type: 'info',
      duration: 3000,
      showClose: true,
    })
  }

  /**
   * Show a warning message toast
   * @param msg - Message text to display
   */
  function showWarning(msg: string) {
    ElMessage({
      message: msg,
      type: 'warning',
      duration: 4000,
      showClose: true,
    })
  }

  return {
    showSuccess,
    showError,
    showInfo,
    showWarning,
  }
}
