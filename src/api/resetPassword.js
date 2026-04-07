import { supabase } from "@/lib/supabase"

/**
 * Request a password reset for the given email. If the email exists, a reset link will be sent.
 * @param {string} email
 * @returns {Promise<{success: boolean, error?: string}>}
 */
export async function requestPasswordReset(email) {
  try {
    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/admin/reset-password-confirm`,
    })
    if (error) return { success: false, error: error.message }
    return { success: true }
  } catch (err) {
    return { success: false, error: err.message }
  }
}
