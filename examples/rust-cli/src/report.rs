use crate::config::CliConfig;

pub struct Report {
    title: String,
    details: Vec<String>,
}

impl Report {
    pub fn render(&self) -> String {
        let mut lines = vec![format!("# {}", self.title)];
        lines.extend(self.details.iter().cloned());
        lines.join("\n")
    }
}

pub fn build_report(config: &CliConfig) -> Report {
    let mut details = vec![format!("project: {}", config.project)];
    if config.verbose {
        details.push("mode: verbose".to_string());
    }
    Report {
        title: "Codeglance Rust Example".to_string(),
        details,
    }
}
