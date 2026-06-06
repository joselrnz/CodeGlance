interface Repo {
  find(id: number): string;
}

export class UserService {
  constructor(private repo: Repo) {}
  load(id: number): string { return this.repo.find(id); }
}

export function makeService(repo: Repo): UserService {
  return new UserService(repo);
}
