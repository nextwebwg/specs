//! Narrow package-only CLI. Arguments are trusted caller evidence, not assertions
//! extracted by this process. No identity authorization or admission is performed.
use email_next_mls_smoke::package_validation::{validate_discovery_package,MAX_PACKAGE_OCTETS};
use std::io::{self,Read};
fn hex32(s:&str)->Result<[u8;32],&'static str>{
    if s.len()!=64 || !s.bytes().all(|b|b.is_ascii_digit()||(b'a'..=b'f').contains(&b)){return Err("argument-hex");}
    let mut out=[0;32];for (i,v) in out.iter_mut().enumerate(){*v=u8::from_str_radix(&s[i*2..i*2+2],16).map_err(|_|"argument-hex")?;}Ok(out)
}
fn decimal(s:&str)->Result<u64,&'static str>{
    if s.is_empty() || (s.len()>1&&s.starts_with('0')) || !s.bytes().all(|b|b.is_ascii_digit()){return Err("argument-time");}
    s.parse().map_err(|_|"argument-time")
}
fn run()->Result<(),&'static str>{
    let args:Vec<String>=std::env::args().skip(1).collect();
    if args.len()!=5{return Err("arguments");}
    let principal=hex32(&args[0])?;let device=hex32(&args[1])?;let key=hex32(&args[2])?;
    let earliest=decimal(&args[3])?;let latest=decimal(&args[4])?;
    // Never read unbounded stdin to discover its size after allocation.
    let mut bytes=Vec::new();io::stdin().lock().take((MAX_PACKAGE_OCTETS+1) as u64).read_to_end(&mut bytes).map_err(|_|"input")?;
    if bytes.len()>MAX_PACKAGE_OCTETS{return Err("size");}
    validate_discovery_package(&bytes,&principal,&device,&key,earliest,latest)?;
    println!("{{\"status\":\"package-valid\"}}");Ok(())
}
fn main(){if let Err(reason)=run(){println!("{{\"status\":\"rejected\",\"reason\":\"{reason}\"}}");std::process::exit(1);}}
