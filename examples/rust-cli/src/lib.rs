pub mod config;
pub mod report;

use config::CliConfig;
use report::Report;

pub fn run(config: CliConfig) -> Report {
    report::build_report(&config)
}
