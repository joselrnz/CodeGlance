mod config;
mod report;

use config::CliConfig;
use report::build_report;

fn main() {
    let config = CliConfig::from_args(std::env::args().collect());
    let report = build_report(&config);
    println!("{}", report.render());
}
