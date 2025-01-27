use crate::errors::{context, err_val_error, ErrorKind, ValResult};

use super::Input;

#[inline]
pub fn str_as_bool<'a>(input: &'a impl Input<'a>, str: &str) -> ValResult<'a, bool> {
    if str == "0"
        || str.eq_ignore_ascii_case("f")
        || str.eq_ignore_ascii_case("n")
        || str.eq_ignore_ascii_case("no")
        || str.eq_ignore_ascii_case("off")
        || str.eq_ignore_ascii_case("false")
    {
        Ok(false)
    } else if str == "1"
        || str.eq_ignore_ascii_case("t")
        || str.eq_ignore_ascii_case("y")
        || str.eq_ignore_ascii_case("on")
        || str.eq_ignore_ascii_case("yes")
        || str.eq_ignore_ascii_case("true")
    {
        Ok(true)
    } else {
        err_val_error!(input_value = input.as_error_value(), kind = ErrorKind::BoolParsing)
    }
}

#[inline]
pub fn int_as_bool<'a>(input: &'a impl Input<'a>, int: i64) -> ValResult<'a, bool> {
    if int == 0 {
        Ok(false)
    } else if int == 1 {
        Ok(true)
    } else {
        err_val_error!(input_value = input.as_error_value(), kind = ErrorKind::BoolParsing)
    }
}

#[inline]
pub fn str_as_int<'s, 'l>(input: &'s impl Input<'s>, str: &'l str) -> ValResult<'s, i64> {
    if let Ok(i) = str.parse::<i64>() {
        Ok(i)
    } else if let Ok(f) = str.parse::<f64>() {
        float_as_int(input, f)
    } else {
        err_val_error!(input_value = input.as_error_value(), kind = ErrorKind::IntParsing)
    }
}

pub fn float_as_int<'a>(input: &'a impl Input<'a>, float: f64) -> ValResult<'a, i64> {
    if float == f64::INFINITY {
        err_val_error!(
            input_value = input.as_error_value(),
            kind = ErrorKind::IntNan,
            context = context!("nan_value" => "infinity")
        )
    } else if float == f64::NEG_INFINITY {
        err_val_error!(
            input_value = input.as_error_value(),
            kind = ErrorKind::IntNan,
            context = context!("nan_value" => "negative infinity")
        )
    } else if float.is_nan() {
        err_val_error!(
            input_value = input.as_error_value(),
            kind = ErrorKind::IntNan,
            context = context!("nan_value" => "NaN")
        )
    } else if float % 1.0 != 0.0 {
        err_val_error!(input_value = input.as_error_value(), kind = ErrorKind::IntFromFloat)
    } else {
        Ok(float as i64)
    }
}
