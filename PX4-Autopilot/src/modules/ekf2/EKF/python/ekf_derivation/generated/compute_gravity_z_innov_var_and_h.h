// -----------------------------------------------------------------------------
// This file was autogenerated by symforce from template:
//     function/FUNCTION.h.jinja
// Do NOT modify by hand.
// -----------------------------------------------------------------------------

#pragma once

#include <matrix/math.hpp>

namespace sym {

/**
 * This function was autogenerated from a symbolic function. Do not modify by hand.
 *
 * Symbolic function: compute_gravity_z_innov_var_and_h
 *
 * Args:
 *     state: Matrix24_1
 *     P: Matrix23_23
 *     R: Scalar
 *
 * Outputs:
 *     innov_var: Scalar
 *     Hz: Matrix23_1
 */
template <typename Scalar>
void ComputeGravityZInnovVarAndH(const matrix::Matrix<Scalar, 24, 1>& state,
                                 const matrix::Matrix<Scalar, 23, 23>& P, const Scalar R,
                                 Scalar* const innov_var = nullptr,
                                 matrix::Matrix<Scalar, 23, 1>* const Hz = nullptr) {
  // Total ops: 18

  // Input arrays

  // Intermediate terms (4)
  const Scalar _tmp0 = 2 * state(2, 0);
  const Scalar _tmp1 = 2 * state(1, 0);
  const Scalar _tmp2 = -_tmp0 * state(3, 0) + _tmp1 * state(0, 0);
  const Scalar _tmp3 = _tmp0 * state(0, 0) + _tmp1 * state(3, 0);

  // Output terms (2)
  if (innov_var != nullptr) {
    Scalar& _innov_var = (*innov_var);

    _innov_var = R + _tmp2 * (P(0, 0) * _tmp2 + P(1, 0) * _tmp3) +
                 _tmp3 * (P(0, 1) * _tmp2 + P(1, 1) * _tmp3);
  }

  if (Hz != nullptr) {
    matrix::Matrix<Scalar, 23, 1>& _hz = (*Hz);

    _hz.setZero();

    _hz(0, 0) = _tmp2;
    _hz(1, 0) = _tmp3;
  }
}  // NOLINT(readability/fn_size)

// NOLINTNEXTLINE(readability/fn_size)
}  // namespace sym
