//! Script-level parameter annotations for SolidCraftForge.
//!
//! `#[cad]` processes `#[parameter]` on constructor arguments, leaving the
//! publicly callable signature untouched. Its body receives the same named
//! variable, now wrapping a symbolic CAD parameter rather than a plain f64.
//! This means `size / 1.5` stays a native SolidCraft expression.

use proc_macro::TokenStream;
use quote::quote;
use syn::{parse_macro_input, parse_quote, FnArg, ImplItem, ItemImpl, Pat, Type};

#[proc_macro_attribute]
pub fn cad(_args: TokenStream, input: TokenStream) -> TokenStream {
    let mut implementation = parse_macro_input!(input as ItemImpl);
    let mut errors = Vec::new();

    for item in &mut implementation.items {
        let ImplItem::Fn(method) = item else { continue };
        let mut initializers = Vec::new();

        for argument in &mut method.sig.inputs {
            let FnArg::Typed(argument) = argument else { continue };
            let had_attribute = argument.attrs.iter()
                .any(|attribute| attribute.path().is_ident("parameter"));
            if !had_attribute { continue }
            argument.attrs.retain(|attribute| !attribute.path().is_ident("parameter"));

            let Pat::Ident(ident) = argument.pat.as_ref() else {
                errors.push(syn::Error::new_spanned(&argument.pat,
                    "#[parameter] requires a simple named argument"));
                continue;
            };
            let Type::Path(ty) = argument.ty.as_ref() else {
                errors.push(syn::Error::new_spanned(&argument.ty,
                    "#[parameter] currently supports only f64"));
                continue;
            };
            if !ty.path.is_ident("f64") {
                errors.push(syn::Error::new_spanned(&argument.ty,
                    "#[parameter] currently supports only f64"));
                continue;
            }
            let name = &ident.ident;
            initializers.push(parse_quote! {
                let #name = ::solidcraftforge::csg::ParamLength::new(
                    stringify!(#name),
                    ::solidcraftforge::cad::Length::mm(#name),
                );
            });
        }
        if !initializers.is_empty() {
            method.block.stmts.splice(0..0, initializers);
        }
    }

    let compile_errors = errors.iter().map(syn::Error::to_compile_error);
    quote! {
        #implementation
        #(#compile_errors)*
    }.into()
}
