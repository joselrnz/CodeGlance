pub struct CliConfig {
    pub project: String,
    pub verbose: bool,
}

impl CliConfig {
    pub fn from_args(args: Vec<String>) -> Self {
        let project = args.get(1).cloned().unwrap_or_else(|| "demo".to_string());
        let verbose = args.iter().any(|arg| arg == "--verbose");
        Self { project, verbose }
    }
}
