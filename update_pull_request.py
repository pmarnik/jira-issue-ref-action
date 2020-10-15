#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 19:41:21 2020

@author: piotrmarnik
"""
from dataclasses import dataclass

from github import Github


import os
import regex
import sys




class MissingConfigurationValue(Exception):
    def __init__(self, key):
        Exception.__init__(self, f"Can not find configuration key {key}")
    


def get_env_or_fail(name):
    if name not in os.environ:
        raise MissingConfigurationValue(name)
        print(f"Can not find value for {name}")
        return None
    return os.environ[name]


jira_issue_pattern = regex.compile("((?<!([A-Za-z]{1,10})-?)[A-Z]+-\d+)")




@dataclass
class Config:
    github_token: str
    repository: str
    pull_number: int
    issue_url_pattern: str
    


def config_from_env():
    
    return Config(
        github_token = get_env_or_fail('GITHUB_TOKEN'),
        repository= get_env_or_fail('ACTION_REPOSITORY'),
        pull_number = int(get_env_or_fail('ACTION_PULL_NUMBER')),
        issue_url_pattern = get_env_or_fail('ACTION_ISSUE_URL_PATTERN')
        )
        
    
def build_references(issue_ids, issue_url_pattern):
    print("Found issue ids:", issue_ids)
    if not issue_ids:
        return None
    result = []
    for id in issue_ids:
        if "{issue_key}" in issue_url_pattern:
            result.append(issue_url_pattern.replace("{issue_key}", id))
        else:
            result.append(issue_url_pattern + id)
    result = ["  * " + r for r in result]
    # result = ["--", "### Refeferences"].extend(result)
    header = ["", "---", "### References:"]
    header.extend(result)
    return "\n".join(header)
    
            
    
    
        
    


class PullRequestUpdater:
    def __init__(self, config):
        self.config = config
        self._github_client = Github(config.github_token)

    def get_info(self):
        repo = self._github_client.get_repo(self.config.repository)
        self.pull_req = repo.get_pull(self.config.pull_number)
        result = []
        result.append(self.pull_req.head.ref)
        result.append(self.pull_req.title)
        if (self.pull_req.body):
            result.append(self.pull_req.body)
        for c in self.pull_req.get_commits():
            result.append(c.commit.message)
        
        return result
    
    def get_issue_ids(self):
        data = self.get_info()
        result = set()
        for text in data:
            for found in jira_issue_pattern.findall(text):
                result.add(found[0])
        return sorted(list(result))   

    def build_references(self):
        return build_references(self.get_issue_ids(), self.config.issue_url_pattern)
    
    def update_pull_request(self):
        print(f"Start looking for ticket references in {self.config.repository} on pull request #{self.config.pull_number}")
        refs = self.build_references()
        if not refs:
            return
        self.pull_req.edit(body = self.pull_req.body + "\n" + refs)
        

if __name__ == '__main__':
    try:
        config = config_from_env()
        updater = PullRequestUpdater(config)
        updater.update_pull_request()
    except Exception as err:
        print(err)
        sys.exit(1)
                
        
                
        
        