pub struct Config {
    pub verbose: bool,
}

impl Config {
    pub fn new() -> Self {
        Config { verbose: false }
    }
}

pub fn run(cfg: &Config) -> bool {
    cfg.verbose
}
